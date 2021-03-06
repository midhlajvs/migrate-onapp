#!/usr/bin/env python

import MySQLdb
import sys
import time 
import config 

#Timestamp and VPS list

timestamp = time.strftime("%Y%m%d-%H%M%S")
file = "vds_list-" + timestamp + ".txt"
vds_all = []

#Find hypervisor ID from the label provided 

def get_hvid(label):

   conn = MySQLdb.connect(host= config.host,
                       user= config.user,
                       passwd= config.passwd,
                       db= config.db )

   cur = conn.cursor()

   cur.execute("select id from hypervisors where label = %s", [label])
   result = cur.fetchall()

   for row in result:
      return row[0]

   cur.close()
   conn.close()

#List the VPS under the specified hypevisor

def get_vds_id(source):

   conn = MySQLdb.connect(host= config.host,
                       user= config.user,
                       passwd= config.passwd,
                       db= config.db )
   
   cur = conn.cursor()
   cur.execute("select id from virtual_machines where hypervisor_id = %s", [source])
   result = cur.fetchall()
   return result

   cur.close()
   conn.close()

#Update the database to destination hypervisor

def update_hv(destiantion, vds_id):

    conn = MySQLdb.connect(host= config.host,
                       user= config.user,
                       passwd= config.passwd,
                       db= config.db )

    cur = conn.cursor()
    cur.execute("update virtual_machines set hypervisor_id = %s where id = %s", (destination, vds_id))
   
    conn.commit() 
    print "   Completed ... !!!  %s  ---->   %s" % (vds_id, destination)
    print "\n"
    cur.close()
    conn.close()

#Print usage

def usage():

  print usage_doc


usage_doc = """

 Usage : migrate-hv.py <source_hypervisor_label> <destination_hypervisor_label> 

 Description : Script to migrate all virtual machines on a hypervisor to another. 

 NOTE : Onapp supports only migrating the virtual machines between hypervisors that has shared data stores exist. This script does not migrate the          data stores or underlying volume group, it either automatically switch over to the online hypervisor if the other goes down or you have to 
       manually migrate the volume group holds the virtual machine data. 
"""


if __name__ == "__main__":
   
    if (len(sys.argv)) != 3:
        usage()
        sys.exit()
 
    source = get_hvid(sys.argv[1])
    destination = get_hvid(sys.argv[2])

    if source is None:
        print "\n   Source Hypervisor Label is Invalid"
        usage()
    elif destination is None:
       print "\n   Destination Hypervisor Label is Invalid"
       usage()
    
    else:

      print " Migrating all virtual machines from  Hypervisor %s to Hypervisor %s ..... \n" % (source, destination)

      vds_list = get_vds_id(source)
      if not vds_list: 
           print "\n    No Virtual Machine exists on the source Hypervisor or it has already been migrated ......!!!!!" 
           usage()
           exit()
 
      for id in vds_list:
           vds_all.append(str(id[0]))
  
      file_open = open(file, "w")
      for id in vds_all:
         file_open.write(id)
         file_open.write("\n")
         print " Migrating the virtual machine %s to Hypervisor %s" %(id, destination)
         update_hv(destination, id) 
      
      file_open.close()
