from locust import events
from time import time
from datetime import datetime
from csv import writer as csv_writer
from io import StringIO
import locust.stats
from locust.runners import WorkerRunner


class TransactionManager:
    """
    Transaction Manager allows transactions spanning multiple tasks to be logged
    using start_transaction and end_transaction methods
    Stats are written to file when using --log-transactions-in-file
    otherwise, two web endpoints are available to collect full and summary stats:
    /stats/transactions/csv and /stats/transactions/all/csv
    when running in master/worker mode, all data is sent to the master during execution
    """

    transactions_filename = ""
    transactions_summary_filename = ""
    flush_size = 100
    field_delimiter = ","
    row_delimiter = "\n"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    transactions = []
    completed_transactions = {}
    user_count = 0
    csv_headers = [
        "start_time",
        "duration",
        "transaction_name",
        "user_count",
        "success",
        "failure_message",
    ]

    def __init__(self):
        self.transaction_count = 0
        self.inprogress_transactions = {}

    def start_transaction(self, transaction_name):
        now = time()
        transaction = {}
        transaction["transaction_name"] = transaction_name
        transaction["start_time"] = now
        transaction["user_count"] = self.runner.user_count if self.runner else 0
        self.inprogress_transactions[transaction_name] = transaction
        return transaction_name

    def end_transaction(self, transaction_name, success=True, failure_message=""):
        now = time()
        t = self.inprogress_transactions[transaction_name]
        t["end_time"] = now
        start_time = t["start_time"]
        t["duration"] = round((now - start_time) * 1000)
        t["success"] = success
        t["failure_message"] = failure_message

        self.transactions.append(
            [
                datetime.fromtimestamp(t["start_time"]).strftime(self.timestamp_format),
                round(t["duration"]),
                t["transaction_name"],
                t["user_count"],
                t["success"],
                t["failure_message"],
            ]
        )

        if t["transaction_name"] not in self.completed_transactions:
            self.completed_transactions[t["transaction_name"]] = []

        self.completed_transactions[t["transaction_name"]].append(t)

        del self.inprogress_transactions[transaction_name]

        if (
            len(self.transactions) >= self.flush_size
            and self.log_transactions_in_file
            and not isinstance(self.env.runner, WorkerRunner)
        ):
            self._flush_to_log()

    @classmethod
    def _command_line_parser(cls, parser):
        group = None
        if parser._action_groups:
            group = next((x for x in parser._action_groups if x.title == "Request statistics options"), None)
        if not group:
            group = parser.add_argument_group(title="Request statistics options")

        group.add_argument(
            "--log-transactions-in-file",
            help="Log transactions in a file rather than using the web ui (added by locust-plugins)",
            action="store_true",
            default=False,
        )

    @classmethod
    def _create_results_log(cls):
        cls.results_file = open(cls.transactions_filename, "w")
        cls.results_file_writer = cls._create_csv_writer(cls.results_file)
        cls.results_file_writer.writerow(cls.csv_headers)
        cls.results_file.flush()

    @classmethod
    def _create_csv_writer(cls, buffer):
        return csv_writer(buffer, delimiter=cls.field_delimiter, lineterminator=cls.row_delimiter)

    @classmethod
    def _flush_to_log(cls):
        cls.results_file_writer.writerows(cls.transactions)
        cls.results_file.flush()
        cls.transactions = []

    @classmethod
    def _write_final_log(cls, **_kwargs):
        if not isinstance(cls.env.runner, WorkerRunner):
            if cls.log_transactions_in_file and not cls.results_file.closed:
                cls.results_file_writer.writerows(cls.transactions)
                cls.results_file.close()
                # also write summary file in stats.py style
                with open(cls.transactions_summary_filename, "w") as f:
                    writer = cls._create_csv_writer(f)
                    writer.writerows(cls._get_transactions_summary())

    @classmethod
    def _init_filenames(cls):
        # determine whether to output to file, (if options parsed)
        if cls.env.parsed_options:
            cls.log_transactions_in_file = cls.env.parsed_options.log_transactions_in_file
            if cls.env.parsed_options.csv_prefix:
                cls.transactions_filename = f"{cls.env.parsed_options.csv_prefix}_transactions.csv"
                cls.transactions_summary_filename = f"{cls.env.parsed_options.csv_prefix}_transactions_summary.csv"
        else:
            cls.log_transactions_in_file = False
        if cls.log_transactions_in_file and not cls.transactions_filename:
            timestamp = datetime.fromtimestamp(time()).strftime("%Y_%m_%d_%H_%M_%S")
            cls.transactions_filename = f"transactions_{timestamp}.csv"
            cls.transactions_summary_filename = f"transactions_summary_{timestamp}.csv"

    @classmethod
    def on_locust_init(cls, environment, runner, **_kwargs):
        cls.env = environment
        cls.runner = runner
        cls._init_filenames()

        if cls.log_transactions_in_file and not isinstance(cls.env.runner, WorkerRunner):
            cls._create_results_log()
        if cls.env.web_ui:
            # this route available if a csv isn't being written to (--log-transactions-in-file is omitted)
            @cls.env.web_ui.app.route("/stats/transactions/all/csv")
            def _transactions_results_page():
                headers = {}
                headers["Content-type"] = "text/csv"
                headers["Content-disposition"] = f"attachment;filename={cls.transactions_filename}"
                with StringIO() as buffer:
                    writer = cls._create_csv_writer(buffer)
                    writer.writerows([cls.csv_headers] + cls.transactions)
                    response = buffer.getvalue()
                return cls.env.web_ui.app.response_class(
                    response=response,
                    headers=headers,
                    status=200,
                    mimetype="text/csv",
                )

            # provides summary stats like requests endpoint
            @cls.env.web_ui.app.route("/stats/transactions/csv")
            def _transactions_summary_page():
                headers = {}
                headers["Content-type"] = "text/csv"
                headers["Content-disposition"] = f"attachment;filename={cls.transactions_summary_filename}"
                with StringIO() as buffer:
                    writer = cls._create_csv_writer(buffer)
                    writer.writerows(cls._get_transactions_summary())
                    response = buffer.getvalue()
                return cls.env.web_ui.app.response_class(
                    response=response,
                    headers=headers,
                    status=200,
                    mimetype="text/csv",
                )

    @classmethod
    def _get_transactions_summary(cls):
        # create a summary in the same format as used for requests in stats.py
        summary = []
        summary.append(
            [
                "Type",
                "Name",
                "Request Count",
                "Failure Count",
                "Median Response Time",
                "Average Response Time",
                "Min Response Time",
                "Max Response Time",
            ]
            + locust.stats.get_readable_percentiles(locust.stats.PERCENTILES_TO_REPORT)
        )
        for tname in cls.completed_transactions:  # pylint: disable=consider-using-dict-items
            fields = []
            # fill the field that holds request method
            fields.append("Transaction")
            fields.append(tname)

            durations = [sub["duration"] for sub in cls.completed_transactions[tname]]
            fields.append(str(len(durations)))

            successes = [sub["success"] for sub in cls.completed_transactions[tname]]
            failure_count = successes.count(False)
            fields.append(str(failure_count))

            sorted_durations = sorted(durations)
            median = sorted_durations[int(0.5 * len(sorted_durations))]
            fields.append(str(median))
            avg = round(sum(sorted_durations) / len(sorted_durations))
            fields.append(str(avg))

            fields.append(str(round(sorted_durations[0])))
            fields.append(str(round(sorted_durations[-1])))
            # loop through the other metrics set out in stats.py
            for p in locust.stats.PERCENTILES_TO_REPORT:
                fields.append(str(sorted_durations[int(p * len(sorted_durations)) - 1]))
            summary.append(fields)
        return summary

    @classmethod
    def _report_to_master(cls, data, **_kwargs):
        data["transactions"] = cls.transactions
        cls.transactions = []
        data["completed_transactions"] = cls.completed_transactions
        cls.completed_transactions = {}

    @classmethod
    def _worker_report(cls, data, **_kwargs):
        if "transactions" in data:
            transactions = data["transactions"]
            cls.transactions += transactions
            completed_transactions = data["completed_transactions"]
            for t in completed_transactions:
                if t not in cls.completed_transactions:
                    cls.completed_transactions[t] = []
                cls.completed_transactions[t] += completed_transactions[t]


events.init.add_listener(TransactionManager.on_locust_init)
events.init_command_line_parser.add_listener(TransactionManager._command_line_parser)
events.report_to_master.add_listener(TransactionManager._report_to_master)
events.worker_report.add_listener(TransactionManager._worker_report)
events.test_stop.add_listener(TransactionManager._write_final_log)
