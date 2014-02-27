# import os, re

# with open('reviews.valid') as f:
#     s = f.read()
#     l = s.split('\n')
#     with open('res.csv','w') as x:
#         for i in l:
#             if len(i) > 0:
#                 x.write(i[0] + ',\n')

with open('res.csv') as x:
    s = x.read()
    s = s.split('\n')
    corr = 0
    total = 280.0
    num_z = 0.0
    num_o = 0.0
    num_z_c = 0
    num_o_c = 0
    for i in s:
        if len(i) > 0 and i[0] == i[2]:
            corr += 1
        if len(i) > 0 and int(i[0]) == 1:
            num_o += 1
            if int(i[2]) == 1:
                num_o_c += 1
        if len(i) > 0 and int(i[0]) == 0:
            num_z += 1
            if int(i[2]) == 0:
                num_z_c += 1
    print "accuracy: " + str(corr/total)
    print "truth acc: " + str(num_o_c/num_o)
    print "false acc: " + str(num_z_c/num_z)