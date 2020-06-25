from locust import events
from time import time
from datetime import datetime
import locust.stats

class TransactionManager:
    """
    Transaction Manager allows transactions spanning multiple tasks to be logged
    using start_transaction and end_transaction methods
    Stats are written to file when using --log_transactions_in_file=True
    otherwise, two web endpoints are available to collect full and summary stats:
    /stats/transactions/csv and /stats/transactions/all/csv
    when running in master/worker mode, all data is sent to the master during execution
    """
    flush_size = 100
    field_delimiter = ","
    row_delimiter = "\n"
    timestamp_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.transaction_count = 0
        self.inprogress_transactions = {}
        self.flat_transaction_list = []
        self.completed_transactions = {}
        # results filename format
        self.test_timestamp = datetime.fromtimestamp(time()).strftime("%Y_%m_%d_%H_%M_%S")
        self.transactions_filename = f"transactions_{self.test_timestamp}.csv"
        self.transactions_summary_filename = f"transactions_summary_{self.test_timestamp}.csv"

        # fields set for file output
        self.csv_headers = [
            "start_time",
            "duration",
            "transaction_name",
            "user_count",
            "success",
            "failure_message",
        ]

        self.user_count = 0
        events.init.add_listener(self._on_locust_init)
        events.init_command_line_parser.add_listener(self._command_line_parser)
        events.worker_report.add_listener(self._worker_report)
        events.report_to_master.add_listener(self._report_to_master)
        events.test_stop.add_listener(self._write_final_log)

    def _command_line_parser(self, parser):
        parser.add_argument(
            "--log_transactions_in_file",
            help="To log transactions in file rather than using the web ui, set to True",
            default=False,
        )
        self.is_not_worker = not parser.parse_args().worker

    def start_transaction(self, transaction_name):
        self.transaction_count += 1
        transaction_id = self.transaction_count
        now = time()
        transaction = {}
        transaction["transaction_id"] = transaction_id
        transaction["transaction_name"] = transaction_name
        transaction["start_time"] = now
        transaction["end_time"] = None
        transaction["duration"] = None
        transaction["success"] = None
        transaction["failure_message"] = None
        transaction["user_count"] = self.runner.user_count if self.runner else 0
        self.inprogress_transactions[transaction_id] = transaction
        return transaction_id

    def end_transaction(self, transaction_id, success=True, failure_message=""):
        now = time()
        t = self.inprogress_transactions[transaction_id]
        t["end_time"] = now
        start_time = t["start_time"]
        t["duration"] = round((now - start_time) * 1000)
        t["success"] = success
        t["failure_message"] = failure_message

        self.flat_transaction_list.append(
            f'{datetime.fromtimestamp(t["start_time"]).strftime(self.timestamp_format)}{self.field_delimiter}'
            f'{round(t["duration"])}{self.field_delimiter}'
            f'{t["transaction_name"]}{self.field_delimiter}'
            f'{t["user_count"]}{self.field_delimiter}'
            f'{t["success"]}{self.field_delimiter}'
            f'{t["failure_message"]}'
        )

        if t["transaction_name"] not in self.completed_transactions:
            self.completed_transactions[t["transaction_name"]] = []

        self.completed_transactions[t["transaction_name"]].append(t)

        del self.inprogress_transactions[transaction_id]

        if len(self.flat_transaction_list) >= self.flush_size and self.log_transactions_in_file and self.is_not_worker:
            self._flush_to_log()

    def _create_results_log(self):
        results_file = open(self.transactions_filename, "w")
        results_file.write(self.field_delimiter.join(self.csv_headers) + self.row_delimiter)
        results_file.flush()
        return results_file

    def _flush_to_log(self):
        self.results_file.write(self.row_delimiter.join(self.flat_transaction_list) + self.row_delimiter)
        self.results_file.flush()
        self.flat_transaction_list = []

    def _write_final_log(self, **_kwargs):
        if self.is_not_worker:
            if self.log_transactions_in_file:
                self.results_file.write(self.row_delimiter.join(self.flat_transaction_list) + self.row_delimiter)
                self.results_file.close()
                # also write summary file in stats.py style
                summary_file = open(self.transactions_summary_filename, "w")
                summary_file.write(self.row_delimiter.join(self.get_transactions_summary()))
                summary_file.close()

    def _on_locust_init(self, environment, runner, **_kwargs):
        self.env = environment
        self.runner = runner
        # determine whether to ouput to file
        self.log_transactions_in_file = self.env.parsed_options.log_transactions_in_file
        if self.log_transactions_in_file and self.is_not_worker:
            self.results_file = self._create_results_log()
        if self.env.web_ui:
            # this route available if a csv isn't being written to (--log_transactions_in_file=False)
            @self.env.web_ui.app.route("/stats/transactions/all/csv")
            def _transactions_results_page():
                headers = {}
                headers["Content-type"] = "text/csv"
                headers["Content-disposition"] = f"attachment;filename={self.transactions_filename}"
                response = self.env.web_ui.app.response_class(
                    response=self.field_delimiter.join(self.csv_headers)
                    + self.row_delimiter
                    + self.row_delimiter.join(self.flat_transaction_list),
                    headers=headers,
                    status=200,
                    mimetype="text/csv",
                )
                return response

            # provides summary stats like requests endpoint
            @self.env.web_ui.app.route("/stats/transactions/csv")
            def _transactions_summary_page():
                response_body = self.get_transactions_summary()
                headers = {}
                headers["Content-type"] = "text/csv"
                headers["Content-disposition"] = f"attachment;filename={self.transactions_summary_filename}"
                response = self.env.web_ui.app.response_class(
                    response=self.row_delimiter.join(response_body), headers=headers, status=200, mimetype="text/csv",
                )
                return response

    def get_transactions_summary(self):
        # create a summary in the same format as used for requests in stats.py
        summary = []
        summary.append(
            self.field_delimiter.join(
                [
                    '"Type"',
                    '"Name"',
                    '"Request Count"',
                    '"Failure Count"',
                    '"Median Response Time"',
                    '"Average Response Time"',
                    '"Min Response Time"',
                    '"Max Response Time"',
                    '"Average Content Size"',
                    '"Requests/s"',
                    '"Failures/s"',
                    '"50%"',
                    '"66%"',
                    '"75%"',
                    '"80%"',
                    '"90%"',
                    '"95%"',
                    '"98%"',
                    '"99%"',
                    '"99.9%"',
                    '"99.99%"',
                    '"99.999%"',
                    '"100%"',
                ]
            )
        )
        for tname in self.completed_transactions:
            fields = []
            # fill the field that holds request method
            fields.append("Transaction")
            fields.append(tname)

            durations = [sub["duration"] for sub in self.completed_transactions[tname]]
            fields.append(str(len(durations)))

            successes = [sub["success"] for sub in self.completed_transactions[tname]]
            failure_count = successes.count(False)
            fields.append(str(failure_count))

            sorted_durations = sorted(durations)
            median = sorted_durations[int(0.5 * len(sorted_durations))]
            fields.append(str(median))
            avg = round(sum(sorted_durations) / len(sorted_durations))
            fields.append(str(avg))

            fields.append(str(round(sorted_durations[0])))
            fields.append(str(round(sorted_durations[-1])))
            # content size is not relevant
            fields.append("")
            # loop throug the other metrics set out in stats.py
            for p in locust.stats.PERCENTILES_TO_REPORT:
                fields.append(str(sorted_durations[int(p * len(sorted_durations)) - 1]))
            summary.append(self.field_delimiter.join(fields))
        return summary

    def _report_to_master(self, data, **_kwargs):
        data["flat_transaction_list"] = self.flat_transaction_list
        self.flat_transaction_list = []
        data["completed_transactions"] = self.completed_transactions
        self.completed_transactions = {}

    def _worker_report(self, data, **_kwargs):
        if "flat_transaction_list" in data:
            flat_transaction_list = data["flat_transaction_list"]
            self.flat_transaction_list += flat_transaction_list
            completed_transactions = data["completed_transactions"]
            for t in completed_transactions:
                if t not in self.completed_transactions:
                    self.completed_transactions[t] = []
                self.completed_transactions[t] += completed_transactions[t]
