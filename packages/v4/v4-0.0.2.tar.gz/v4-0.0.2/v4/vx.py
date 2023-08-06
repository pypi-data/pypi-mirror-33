from __future__ import print_function, division
import os
import subprocess
import re
from numpy  import *
import sys

import string

#### Image pixel types 
# uint8 VX_PCHAR   
# int16 VX_PINT
# int32 VX_PLONG
# float32 VX_FLOAT
# float64 VX_DOUBLE
def vxparse (argv, opt):
    av=' '.join(argv)
    cmd= "vshparse " + opt + " with " + av
    out=subprocess.check_output( cmd, shell=True)
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    #out, _ = p.communicate()
    #### python does not like a variable name "if" change to "vxif"
    olist = re.sub("if=", "vxif=", out )
    return olist


def vfread ( file ):
   tname = file + ".npy"
   os.system("vxtonpy if=" + file + " of=" + tname)
   a = load( tname )
   os.system("rm " + tname)
   return a

def v3fread ( file ):
   tname = file + ".npy"
   os.system("vxtonpy if=" + file + " of=" + tname)
   a = load( tname )
   os.system("rm " + tname)
   return a

def vfwrite (file, arg):
   tname = file + ".npy"
   save(tname, arg)
   os.system("vnpytovx if=" + tname + " of=" + file)
   os.system("rm " + tname)
   return

def v3fwrite (file, arg):
   tname = file + ".npy"
   save(tname, arg)
   os.system("vnpytovx if=" + tname + " of=" + file)
   os.system("rm " + tname)
   return

def vfembed (img, xlo, xhi, ylo, yhi):
    stm = (ylo + yhi + img.shape[0], xlo + xhi + img.shape[1])
    tm = zeros( stm, dtype=uint8)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            tm[y+ylo,x+xlo] = img[y,x]
    return tm

def v3fembed (img, xlo, xhi, ylo, yhi,zlo,zhi):
    stm = (zlo +zhi + img.shape[0], ylo + yhi + img.shape[1],
          xlo + xhi + img.shape[2])
    tm = zeros( stm, dtype=uint8)
    for z in range(img.shape[0]):
        for y in range(img.shape[1]):
            for x in range(img.shape[2]):
                tm[z+zlo][y+ylo,x+xlo] = img[z,y,x]
    return tm

def vfnewim ( type, bbx, chan ):
    if type == 1 or type=="VX_PCHAN":
        type = 'uint8'
    stm = (bbx[3] , bbx[1] * chan)
    tm = zeros( stm, dtype=type)
    return tm

def v3fnewim ( type, bbx, chan ):
    if type == 1 or type == "VX_PCHAN":
        type = 'uint8'
    stm = (bbx[5] , bbx[3], bbx[1] * chan)
    tm = zeros( stm, dtype=type)
    return tm

class Vx:
   def __init__(self, *args):
     if 0 == len(args) :
        self.i = zeros([0,0],'uint8')
        self.h = ''
        self.c = 1
        return
     if 1 == len(args) :
       # read image file
       rfile = args[0]
       if isinstance (rfile, str) :
        self.ofile = rfile
        __pfix = rfile
        if len(rfile)  == 0 :
              __pfix = "VX.py"
        tname = __pfix +  ".npy"
        hname = __pfix +  ".pyhdr"
        os.system("vxtonpy if=" + rfile + " of=" + tname + " oh=" + hname)
        self.i = load( tname)
        self.h=open(hname).read()
        os.system("rm " + tname + " " + hname)
        __meta =  [i for i in self.h.split('\n') if i != ''][-1]
        self.c = int(__meta.split('=')[1].split(',')[0])
        if self.c != 1 :
            __oshape = self.i.shape
            __nshape = (__oshape[:-1]) + ( __oshape[-1]/self.c, self.c)
            self.i = reshape(self.i, __nshape)
       else :
        self.i = rfile.i
        self.h = rfile.h
        self.c = rfile.c
     if 3 == len(args) or 2 == len(args):
        # implicit creation
        ptype = args[0]
        if not ptype in ("uint8","int8","int16","int32","float32","float64") :
          print ('error: type not supported')
          return
        bbx = args[1]
        if 2 == len(args) :
           chan = 1
        else :
           chan = args[2]
        self.c = chan
        if len(bbx) == 4 :
            if (chan != 1):
                stm = (bbx[3] , bbx[1],  chan)
            else:
                stm = (bbx[3] , bbx[1] )
        elif len(bbx) == 6 :
            if (chan != 1):
                stm = (bbx[5] , bbx[3], bbx[1], chan)
            else:
                stm = (bbx[5], bbx[3] , bbx[1])
        else :
            print ('error: bounding box has wrong length')
            return
        self.h=""
        # if c != 1 then reshape
        self.i = zeros( stm, dtype=ptype)
        # if c != 1 then reshape
   def __repr__(self):
        fmt_str = 'VisionX V4: ' + self.__class__.__name__ + '\n'
        fmt_str += '    Image Size: {}\n'.format(self.i.shape)
        fmt_str += '    Pixel Type: {}\n'.format(self.i.dtype)
        fmt_str += '    Number of channels: {}\n'.format(self.c)
        #fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        #tmp = 'train' if self.train is True else 'test'
        #fmt_str += '    Split: {}\n'.format(tmp)
        #fmt_str += '    Root Location: {}\n'.format(self.root)
        #tmp = '    Transforms (if any): '
        #fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        #tmp = '    Target Transforms (if any): '
        #fmt_str += '{0}{1}'.format(tmp, self.target_transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str
   def  write(self, wfile):
        __pfix = wfile
        if len(wfile)  == 0 :
              __pfix = "VX.py"
        txname = __pfix  + ".pyhist"
        tfile  = open( txname, "w")
        tfile.write ( self.h )
        s=' '
        args= s.join(sys.argv)
        tfile.write ( args )
        tfile.close()
        tname = __pfix  + ".npy"
        if self.c != 1 : 
            __oshape = self.i.shape
            __nshape = (__oshape[:-2]) + ( __oshape[-1] * __oshape[-2],) 
            __tmpi = reshape(self.i, __nshape)
            save(tname, __tmpi)
            del __tmpi
        else :
            save(tname, self.i)
        os.system("vnpytovx if=" + tname + " of=" + wfile + ',t="' + args + '" ih=' + txname + " c=" + str(self.c))
        os.system("rm " + tname + " " + txname)
   def  setim(self, imarray ):
        self.i = imarray
   def  embedim(self, vals ):
          vxin = self.i
          xlo=0
          ylo=0
          zlo=0
          __sh = self.i.shape
          __dim= self.i.ndim
          __lshape = len(vals)
          if __dim == 2 :
              if __lshape != 4 : 
                 print ('error: wrong number of offsets"')
                 return
              else:
                 ylo=vals[2]
                 xlo=vals[0]
                 yhi=vals[3]
                 xhi=vals[1]
                 stm = (ylo + yhi + self.i.shape[0], xlo +xhi + self.i.shape[1])
                 self.i =  zeros( stm, dtype=self.i.dtype)
                 for y in range(vxin.shape[0]):
                     for x in range(vxin.shape[1]):
                        self.i[y+ylo,x+xlo] = vxin[y,x]
          else:
              if __lshape != 6 : 
                 print ('error: wrong number of offsets')
                 return
              else:
                 zlo=vals[4]
                 ylo=vals[2]
                 xlo=vals[0]
                 zhi=vals[5]
                 yhi=vals[3]
                 xhi=vals[1]
                 stm = (zlo +zhi + self.i.shape[0], ylo + yhi + self.i.shape[1],
                       xlo + xhi + self.i.shape[2])
                 self.i = zeros( stm, dtype=vxin.dtype )
                 for z in range(vxin.shape[0]):
                     for y in range(vxin.shape[1]):
                       for x in range(vxin.shape[2]):
                         self.i[z+zlo,y+ylo,x+xlo] = vxin[z,y,x]
def vxcom (__arg):
    __a = string.replace(string.replace(__arg, "{","'+str(",),"}",")+'")
    __b = "'" + __a + "'"
    return subprocess.check_output( eval(__b), shell=True)
def vcom (__arg):
    return subprocess.check_output( __arg, stderr=subprocess.STDOUT, shell=True)
def vsub ( arg ) :
    b = string.replace(string.replace(arg, "{","'+str(",),"}",")+'")
    return ( "'" + b + "'")

__VXtmp = [];
__VXtmc = 1;
def VXtclean ( ):
    global __VXtmp, __VXtmc;
    for i in __VXtmp:
        vcom ( 'rm -f '+ i)
    __VXtmp = [];
    
def vdovar (arg ):
    global __VXtmp, __VXtmc;
    atype = type(arg).__name__;
    #print atype;
    if -1 != str.find('int float long double', atype):
        return str(arg);
    elif atype == 'str':
        if arg == '__VXtmp' :   #this is an of=
            tmname = 'tmp.vxpy.'+ str(os.getpid()) + '.'+ str(__VXtmc);
            __VXtmc += 1;
            __VXtmp.append(tmname);
            return tmname;
        else:
            return arg;
    elif atype == 'instance' :
        if isinstance(arg, Vx):
            #print 'VX found'
            #create tmp name
            tmname = 'tmp.vxpy.'+ str(os.getpid()) + '.'+ str(__VXtmc);
            __VXtmc += 1;
            __VXtmp.append(tmname);
            #write file to tmp name
            arg.write(tmname);
            #return tmp name
            return tmname;
        else:
            raise ValueError ('vdovar VX' + atype)
    else: 
        raise ValueError ('vdovar ' + atype)
    return 'X'+ arg+'X'

def vxsh ( arg ):
    a = str.split(arg, ' ')
    plist='vx.vcom( '
    polist='\');vx.VXtclean();'
    dolist='\''
    # chk for assignment, start name = ...
    pl = str.split(arg, '=')
    if len(pl) > 1 :
        wd = str.strip(pl[0])
        if -1 == str.find(wd, ' '):
            plist = wd + ' = ' + plist;
            pl.pop(0);
            a = str.split('='.join(pl));
    for i in a:
        if -1 != str.find(i, '$'):
            j = str.split (i, '$');
            #print 'found ', j[0]
            #find if of=
            if j[0] == 'of=':
                polist='\'); ' + j[1] + ' = vx.Vx(vx.__VXtmp[-1]);vx.VXtclean();'
                dolist += ' ' + j[0] + '\' + vx.vdovar("__VXtmp") + \''
            else:
                dolist += ' ' + j[0] + '\' + vx.vdovar(' + j[1] + ') + \''
        else:
            dolist += ' ' + i
            #print i
    return plist + dolist + polist;
