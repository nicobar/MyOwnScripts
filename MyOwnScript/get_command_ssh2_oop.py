import pexpect
import json

class remote_cmd:
    def __init__(self, conn_filename):
        
        self.conn_filename = conn_filename
        self.data_conn = self.__get_conn_data()
        self.node_name_list = self.__get_node_name_list()

    def populate_dir_with_show_command(self):
 
        cmd_dict = {cmd: "_".join(cmd.split(" ")) for cmd in self.data_conn[0]["cmd_list"]}
        
        for node in self.node_name_list:
            if node is not "":
                for command in cmd_dict:
                    self.__get_remote_cmd(node, command, cmd_dict[command])  

    def __get_conn_data(self):
        with open (self.conn_filename) as f:
            return json.load(f)
        
    def __get_node_name_list(self):
        with open(self.data_conn[0]["base_dir"] + self.data_conn[0]["device_names_file"], 'r') as fin:
            l_s = fin.readlines()
        return  [ s.strip("\r\n") for s in l_s]       
    
    def __get_remote_cmd(self, node_name, cmd, fname):
        ''' This function read devices names from file,
         connects to them and write on file output of a file '''
    
        cmd_ssh_bridge = 'ssh -y ' + self.data_conn[0]["myusername"] + '@' + self.data_conn[0]["bridge_name"]  
        cmd_telnet_node = 'telnet ' + node_name
        file_name = node_name + '_' + fname + '.txt'
        string_to_expect = str.upper(node_name)  + '#'
                
        child = pexpect.spawn(cmd_ssh_bridge, encoding='utf-8', codec_errors='replace')
    
        child.expect('Password: ')
        child.sendline(self.data_conn[0]["mybridgepwd"])
        child.expect('\$')
    
        child.sendline(cmd_telnet_node)
        child.expect('username: ')
        child.sendline(self.data_conn[0]["myusername"])
        child.expect('password: ')
        child.sendline(self.data_conn[0]["mytacacspwd"])
        child.expect(string_to_expect)
        child.sendline('term len 0')
        child.expect(string_to_expect)
    
        child.sendline(cmd)
    
        with open(self.data_conn[0]["base_dir"] + file_name, 'w') as fout:
            child.logfile_read = fout
            child.expect(string_to_expect)
    
        child.terminate()




#### MAIN ###

# cat /mnt/hgfs/VM_shared/MyOwnScripts/getcommand/conn_data.txt
# [{
#   "bridge_name": "10.192.10.8",
#   "myusername": "zzasp70",
#   "mybridgepwd": "S!Pr0094",
#   "mytacacspwd": "!SPra0094",
#   "base_dir": "/mnt/hgfs/VM_shared/MyOwnScripts/getcommand/", 
#   "device_names_file": "devices_XR_unique_sorted.txt",
#   "cmd_list":  [
#                 "show rpl route-policy",
#                 "show rpl community-set"
#                 ]
# }]

create_show_cmd_files = remote_cmd('/mnt/hgfs/VM_shared/MyOwnScripts/getcommand/conn_data.txt')
create_show_cmd_files.populate_dir_with_show_command()