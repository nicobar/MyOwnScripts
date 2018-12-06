import pexpect
import json
import ciscoconfparse as c
from os import listdir
from os.path import isfile, join

class remote_cmd:
    def __init__(self, conn_filename):
        
        self.conn_filename = conn_filename
        self.json_data = self.__get_json_data()
        self.node_name_list = self.__get_node_name_list()

    def populate_dir_with_show_command(self):
 
        cmd_dict = {cmd: "_".join(cmd.split(" ")) for cmd in self.json_data[0]["cmd_list"]}
        
        for node in self.node_name_list:
            if node is not "":
                for command in cmd_dict:
                    self.__get_remote_cmd(node, command, cmd_dict[command])  

    def __get_json_data(self):
        with open (self.conn_filename) as f:
            return json.load(f)
        
    def __get_node_name_list(self):
        with open(self.json_data[0]["base_dir"] + self.json_data[0]["device_names_file"], 'r') as fin:
            l_s = fin.readlines()
        return  [ s.strip("\r\n") for s in l_s]       
    
    def __get_remote_cmd(self, node_name, cmd, fname):
        ''' This function read devices names from file,
         connects to them and write on file output of a file '''
    
        cmd_ssh_bridge = 'ssh -y ' + self.json_data[0]["myusername"] + '@' + self.json_data[0]["bridge_name"]  
        cmd_telnet_node = 'telnet ' + node_name
        file_name = node_name + '_' + fname + '.txt'
        string_to_expect = str.upper(node_name)  + '#'
                
        child = pexpect.spawn(cmd_ssh_bridge, encoding='utf-8', codec_errors='replace')
    
        child.expect('Password: ')
        child.sendline(self.json_data[0]["mybridgepwd"])
        child.expect('\$')
    
        child.sendline(cmd_telnet_node)
#         if "vce" in node_name or "vsw" in node_name:
#             child.expect('login: ')
#         else:
        child.expect('login: ')
        child.sendline(self.json_data[0]["myusername"])
        child.expect('Password: ')
        child.sendline(self.json_data[0]["mytacacspwd"])
        child.expect(string_to_expect)
        child.sendline('term len 0')
        child.expect(string_to_expect)
    
        child.sendline(cmd)
    
        with open(self.json_data[0]["base_dir"] + file_name, 'w') as fout:
            child.logfile_read = fout
            child.expect(string_to_expect)
    
        child.terminate()

class text_analisys:
    
    def __init__(self, conn_filename):
        self.conn_filename = conn_filename
        self.json_data = self.__get_json_data()
        #self.json_data[0]["base_dir"]
        
    def __get_json_data(self):
        with open (self.conn_filename) as f:
            return json.load(f)
        
    def create_output_vpe(self):
        ''' from <switches_>_command files creates output_commnad file
        with "<switch> command output" as lines '''

        file_list = [f for f in listdir(self.json_data[0]["base_dir"]) if isfile(join(self.json_data[0]["base_dir"], f)) and "VPE" in f]
        for file in file_list:
            #input_file_name = base_dir + file
            list_f = file.split('_')
            node = list_f[0]
    
            #cmd_list = file_list[2:-1] + [file_list[-1:][0][:-4]]
            #cmd_string = '_'.join(cmd_list)
            #output_file_name = base_dir + 'output_' + cmd_string + '.txt'
            with open(self.json_data[0]["base_dir"] + file, 'r') as fin:
                input_text_list = fin.readlines()
            with open(self.json_data[0]["base_dir"] + self.json_data[0]["output_file_name"], 'a') as fout:              
                for line in input_text_list[3:-1]:
                    if len(input_text_list) >3:
                        stripped_line = line.strip()
                        #line_list = stripped_line.split()
                        rd = stripped_line.split(';')[1][4:]
                        right_line = node + ' ' + rd + '\n'                 
                    else:
                        right_line = node + ' ' + 'None\n'
                    fout.write(right_line)
        print('end writing')

    def create_output_osw(self):
        ''' from <switches_>_command files creates output_commnad file
        with "<switch> command output" as lines '''

        text_list = []
        file_list = [f for f in listdir(self.json_data[0]["base_dir"]) if isfile(join(self.json_data[0]["base_dir"], f)) and "OSW" in f]
        for file in file_list:
           
            list_f = file.split('_')
            node = list_f[0]
            
            cfg = self.json_data[0]["base_dir"] + file
            parse = c.CiscoConfParse(cfg)
            obj_if_list = parse.find_objects_w_child('^interface .*Ethernet', 'service-policy')
            
            if len(obj_if_list) > 0:
                for obj_if in obj_if_list:
                    line = node + " " + obj_if.text
                    for obj_if_child in obj_if.all_children:
                        if "service-policy" in  obj_if_child.text:
                            line = line + "\t" + obj_if_child.text 
                    text_list.append(line)
        text = '\n'.join(text_list)
        print(text)
        with open(self.json_data[0]["base_dir"] + self.json_data[0]["output_file_name"], 'a') as fout:              
            fout.write(text)
        print('end writing')

    def create_output_vce(self):
        ''' from <switches_>_command files creates output_commnad file
        with "<switch> command output" as lines '''

        text_list = []
        file_list = [f for f in listdir(self.json_data[0]["base_dir"]) if isfile(join(self.json_data[0]["base_dir"], f)) and "VCE" in f]
        for file in file_list:
           
            list_f = file.split('_')
            node = list_f[0]
            
            cfg = self.json_data[0]["base_dir"] + file
            parse = c.CiscoConfParse(cfg)
            obj_if_list = parse.find_objects_w_child(r'^interface Ethernet', r'ip address')
            
            if len(obj_if_list) > 0:
                for obj_if in obj_if_list:
                    line = node + " " + obj_if.text
                    for obj_if_child in obj_if.all_children:
                        if "area" in  obj_if_child.text:
                            line = line + "\t" + obj_if_child.text 
                    text_list.append(line)
        text = '\n'.join(text_list)
        print(text)
        with open(self.json_data[0]["base_dir"] + self.json_data[0]["output_file_name"], 'a') as fout:              
            fout.write(text)
        print('end writing')

#### MAIN ###

# cat /mnt/hgfs/VM_shared/MyOwnScripts/get_rd/conn_data.txt
# [{
#   "bridge_name": "10.192.10.8",
#   "myusername": "zzasp70",
#   "mybridgepwd": "S!Pr0094",
#   "mytacacspwd": "SPra0!094",
#   "base_dir": "/mnt/hgfs/VM_shared/MyOwnScripts/get_rd/", 
#   "device_names_file": "show_isis_db_uniq_vpeonly.txt",
#   "output_file_name": "output_rd.txt",
#   "comment1": "show bgp vrf OPNET process | i Distinguisher",
#   "cmd_list":  [
#                 "show vrf OPNET detail | i RD"
#                ]
# }]

if __name__ == "__main__":
    
    json_file = '/mnt/hgfs/VM_shared/MyOwnScripts/get_vce_routed_if/conn_data.json'
#    create_show_cmd_files = remote_cmd(json_file)
#    create_show_cmd_files.populate_dir_with_show_command()
    testo = text_analisys(json_file)
    testo.create_output_vce()