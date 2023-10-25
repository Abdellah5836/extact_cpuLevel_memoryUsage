from netmiko import Netmiko
import re
import pandas as pd
# from adding_devices import adding_devices

def adding_devices():
    print("\nThe code bellow needs a file name, the file name must contain all the devices you want to connect to.")
    file_name = input("File Name (supported: xlsx, csv): ")
    xlsxExtension = 'xlsx'
    csvExtension = 'csv'
    pattern01 = r'[\w\.-_]+\.' + xlsxExtension + '$'
    pattern02 = r'[\w\.-_]+\.' + csvExtension + '$'
    if re.match(pattern01, file_name):
    # query01 = input("\nFile extension: ")
        devicesList = list()
        # if query01.lower() == "xlsx":
        try:
            df01 = pd.read_excel(file_name)
            df01.drop(columns=['Unnamed: 0'], inplace=True)        
            devicesList = df01.to_dict(orient='records')
        except Exception as e:
            print(e)

    elif re.match(pattern02, file_name):
        try:
            df02 = pd.read_csv(file_name)
            df02.drop(columns=['Unnamed: 0'], inplace=True)
            devicesList = df02.to_dict(orient='records')
        except Exception as a:
            print(a)
            
    else:
        return "[!] Not sure what kind of file extension is that. (supported: xlsx, csv)"
    
    return devicesList


def cpu_level():
    deviceList = adding_devices()
    ip_list, cpu_5sec, cpu_1min, cpu_5min, cpu_riskList = ([] for i in range(5))
    command = "show processes cpu"
    
    for ip in deviceList:
        try:
            print(f"\n----- Connecting to {ip['host']} -----")
            net_connect = Netmiko(**ip)
            net_connect.enable()

            output = net_connect.send_command(command)

            sec5Pattern = r"CPU utilization for five seconds\:\s(\d+)\%\/(\d+\%)"
            re_5sec = re.search(sec5Pattern, output) if sec5Pattern else None
            re_5sec = re_5sec.group(1)

            min1Pattern = r"one minute:\s(\d+)\%"
            re_1min = re.search(min1Pattern, output) if min1Pattern else None
            re_1min = re_1min.group(1)

            min2Pattern = r"five minutes:\s(\d+)\%"
            re_5min = re.search(min2Pattern, output) if min2Pattern else None
            re_5min = re_5min.group(1)

            ip_list.append(ip['host'])
            cpu_5sec.append(re_5sec + "%")
            cpu_1min.append(re_1min + "%")
            cpu_5min.append(re_5min + "%")

            if int(re_5min) > 90:
                cpu_risk = "Fatal CPU Level"
            elif 70 < int(re_5min) < 90:
                cpu_risk = "High CPU Level"
            else:
                cpu_risk = "No Risk"
            
            cpu_riskList.append(cpu_risk)

        except Exception:
            print(f"\n**** Cannot connect to {ip['host']} ****\n")
        else:
            df = pd.DataFrame({'IP Address': ip_list, 'CPU Levels for 5 seconds': cpu_5sec, 'CPU Risk for 1 Minute': cpu_1min, 'CPU Level for 5 Minutes': cpu_5min,
                               'CPU Risk': cpu_riskList})
            df.to_excel('cpu_levels.xlsx', sheet_name="cpu levels", index=False)
            print("\n**** EOL ****\n")



def memory_usage():
    to_gbps = 1000000
    device_list01 = adding_devices()
    ip_list, totalMemoryList, usedMemoryList, freeMemoryList, riskMememoryList = ([] for i in range(5))
    command = "show processes memory"

    for ip in device_list01:
        try:
            print(f"\n**** Connecting to {ip['host']} ****\n")
            net_connect = Netmiko(**ip)
            net_connect.enable()
            memoryOutput = net_connect.send_command(command)

            patternTotal = r'Processor Pool Total:\s+?(\d+)'
            totalusage = re.search(patternTotal, memoryOutput)
            totalusage = totalusage.group(1)
            totalusage = int(totalusage) // to_gbps

            patternUsed = r'Used:\s+?(\d+)'
            usedusage = re.search(patternUsed, memoryOutput)
            usedusage = usedusage.group(1)
            usedusage = int(usedusage) // to_gbps

            patternFree = r'Free:\s+?(\d+)'
            freeusage = re.search(patternFree, memoryOutput)
            freeusage = freeusage.group(1)
            freeusage = int(freeusage) // to_gbps

            ip_list.append(ip['host'])
            totalMemoryList.append(str(totalusage) + "Gbps")
            usedMemoryList.append(str(usedusage) + "Gbps")
            freeMemoryList.append(str(freeusage) + "Gbps")
            

            memory_usage_percentage = (usedusage / totalusage) * 100
            if memory_usage_percentage > 90:
                riskusage = "Fatal Memory Usage"
            elif 70 < memory_usage_percentage < 90:
                riskusage = "High Memory Usage"
            else:
                riskusage = "No Risk"
            
            riskMememoryList.append(riskusage)

        except Exception as e:
            print(e)
            # print(f"\n**** Cannot connect to {ip['host']} ****\n")
        else:
            df = pd.DataFrame({'IP Address': ip_list, 'Total Memory Usage': totalMemoryList, 'Used Memory Usage': usedMemoryList, 'Free Memory Usage': freeMemoryList,
                               'Memory Risk': riskMememoryList})
            df.to_excel('memoryUsages.xlsx', sheet_name="memory usage", index=False)
            print("\n**** EOL ****\n")


