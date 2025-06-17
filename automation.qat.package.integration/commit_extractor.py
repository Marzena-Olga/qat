import sys

def get_table_trd(argv):

    with open(argv, 'r') as file:
        lines = file.readlines()

    revision = list()
    t = False
    for i in lines:
        if i.find("## Revision History") != -1:    #select text beetween "Revision History" and "Overview"
        #if i.find("| ---------- |: ") != -1:
            t = True
        if i.find("## Overview") != -1:
            t = False
        if t is True:
            i = i.strip()               #Remove wite chars
            if i != '':
                revision.append(i)      #add only lines with text

    #for i in revision:
    #    print(i)

    revision = revision[3:]                     #remove first three lines
    commit = revision[0]                        #choose newest line
    previous_commit = revision[1]
    previous_commit_no = previous_commit.split('|')
    prev_ver = previous_commit_no[3]
    prev_ver = prev_ver.strip()
    header = revision[0]
    header = header.split("<br>")
    header = header[0]
    header = header.strip()
    commit = commit.replace(header, "")
    header = header.replace("|", "")
    header_tmp = header.split(' ')
    header = list()
    for i in header_tmp:
        if i != '':
            header.append(i)
    h = 'Qatlib: {3} release: \nChanges from {4} to {3}:\nDate: {0} {1}, Version: {3}\n'.format(header[0], header[1], header[2], header[3], prev_ver)

    commit = (commit.replace("|", ""))          #remove | chars
    commit = (commit.replace("<br>", " "))      #remove <br> string
    commit = commit.strip()                     #remove white signs at begining and end
    commit = commit.replace(" -", "\n-")        #add new line intstead "-"
    commit = commit + "\n \n"
    footer = "Sign-off-by Marzena Kupniewska <marzena.kupniewska@intel.com> "
    commit = h + commit #+ footer
    #with open('commit.txt', 'w') as file:
        #file.write(commit)
    return commit

if __name__ == '__main__':
    comm = get_table_trd(sys.argv[1])
    print(comm)
