from locust import User, task, between
import greenlet
# from tnz.py3270 import Emulator
from py3270 import Emulator
import random
import os
# import nest_asyncio
# nest_asyncio.apply()
import locust.stats
from pprint import pprint

from locust_plugins.users.tn3270 import tn3270User

locust.stats.CONSOLE_STATS_INTERVAL_SEC = 99999999

USER_CREDENTIALS = [
    ("locust9", "welcome9"),
    ("locust8", "welcome8"),
    ("locust7", "welcome7"),
    ("locust6", "welcome6"),
    ("locust5", "welcome5"),
    ("locust4", "welcome4"),
    ("locust3", "welcome3"),
    ("locust2", "welcome2"),
    ("locust1", "welcome1"),
    ("locust0", "welcome0"),
]

def print_screen(emulator):
    # Retrieve the screen content
    screen_content = emulator.screen()

    # Print the screen content
    print(screen_content)
                
class CSRTUser(tn3270User):

    def on_start(self):
        def string_wait(string):
            while True:
                self.em.wait_for_field()
                c = self.em.exec_command(b"Ascii()")
                if string in b"\n".join(c.data).decode():
                    return
        #user_id = random.randint(0,999)
        if len(USER_CREDENTIALS) > 0:
            self.user, self.passw = USER_CREDENTIALS.pop()

        self.logfile = str(self.user) + ".log"

        print(str(self.user) + " initiating Telnet session!")
        self.em = Emulator(visible=False, args=["-trace",
                                  "-tracefile",
                                  self.logfile])
        
        self.em.connect('y:%s:%d' % (self.host, 23))

        print(str(self.user) + " connected to " + str(self.host))
        self.em.wait_for_field()
        self.screenshot = str(self.user) + "-screen.html"
        self.em.save_screen(self.screenshot)
        
        string_wait("Application")
        self.em.wait_for_field()
        self.em.send_string("TSO")
        self.em.save_screen(self.screenshot)
        self.em.send_enter()

        # Enter user ID
        string_wait("ENTER USERID")
        self.em.wait_for_field()
        self.em.send_string(str(self.user))
        self.em.save_screen(self.screenshot)
        self.em.send_enter()

        # Enter password
        string_wait("Password  ===>")
        self.em.wait_for_field()
        self.em.wait_for_field()
        self.em.send_string(str(self.passw))
        self.em.send_enter()
        self.em.send_enter()
        self.em.save_screen(self.screenshot)

        # Enter ISPF
        string_wait("READY")
        print(str(self.user) + " successfully logged on! ")
        pprint(self.em.exec_command("PrintText(string)").data)
        self.em.send_enter()
        self.em.wait_for_field()
        self.em.send_string('SDSF')
        self.em.send_enter()
        self.em.save_screen(self.screenshot)

        # Access 3.4 panel on ISPF
        # string_wait("z/OS Primary Option Menu")
        # self.em.wait_for_field()
        # self.em.send_string('3.4')
        # self.em.send_enter()
        # self.em.save_screen(self.screenshot)
        self.em.wait_for_field()
        self.em.send_pf3()
        self.em.send_pf3()
        self.em.send_pf3()
        

    def on_stop(self):
        # self.em.pf3()
        # self.em.pf3()
        # self.em.pf3()
        # string_wait("READY")
        # self.em.send_clear()
        # self.em.send_enter()
        # self.em.send_string("LOGOFF")
        # self.em.send_enter()
        self.em.terminate()
        os.remove(self.logfile)
        os.remove(self.screenshot)


    def run_command(self):
        def string_wait(string):
            while True:
                self.em.wait_for_field()
                c = self.em.exec_command(b"Ascii()")
        # string_wait("READY")
        self.em.wait_for_field()    
        self.em.save_screen(self.screenshot)
        print(str(self.user) + " sending random TSO command")
        self.em.send_string(random.choice(["LU " + str(self.user),"LISTDS 'RAHMAN.K2.JCL' MEMBERS"]))
        # self.em.send_string("LU " + str(self.user))
        self.em.send_enter()
        self.em.send_enter()
        self.em.send_enter()
        self.em.send_enter()
        self.em.send_enter()
       # pprint(self.em.exec_command("PrintText(string)").data)

        
        # string_wait("ENTER PASSWORD:")
        # self.em.wait_for_field()
        # self.em.send_string("welcome0")
        # self.em.send_enter()
        # self.em.send_enter()
        # self.em.send_enter()
        # self.em.send_string("sdsf")
        # string_wait("TEST")
        # self.em.PrintWindow()
        # # response = self.em.string_get()
        # self.em.terminate()
        # validate response or raise an exception

    @task
    def do_async(self):
        self.run_command()
