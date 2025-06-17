import re
import sys

reg = '(((qat)(_upstream|_[0-9]\.[0-9](\.[0-9])?))?(_(lin|win|vmw|bsd|xse|all)_)?(main|master|next|rel_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]{0,30}|(protected_)?dev_[a-zA-z0-9\_]{1,30}|mirror_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]*)$)'

def check_regex(string, reg):
    pattern = re.compile(reg)
    #pattern = re.compile('((qat)(_upstream|_[0-9].[0-9](\.[0-9])?))?(_(lin|win|vmw|bsd|xse|all)_)?(main|master|next|rel_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]{0,30}|(protected_)?dev_[a-zA-z0-9\_]{1,30}|mirror_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]*)*')
    print(pattern.match(string))
    res = (pattern.match(string))
    if res is None:
        print('ERROR: String is not in regex')
        return 255
    else:
        if (res.string)  == string:
            print('String is OK')
            return 0

if __name__ == '__main__':
    string = sys.argv[1]
    #string = 'qat_upstream_lin_rel_24.02.0'
    res = check_regex(string, reg)
    if res != 0:
        sys.exit(-1)