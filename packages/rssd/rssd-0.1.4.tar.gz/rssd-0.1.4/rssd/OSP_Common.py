#####################################################################
### Rohde & Schwarz Automation for demonstration use.
###
### Purpose: OSP Open Switch Platform Common Functions
### Author:  Martin C Lim
### Date:    2018.06.15
### Strctr : pyvisa-->yavisa-->OSP_Common.py
#####################################################################
from yaVISA import jaVisa

class OSP(jaVisa):
   def __init__(self):
      super(OSP, self).__init__()
      self.Model = "OSP1x0"
             
   #####################################################################
   ### OSP Switching Functions
   #####################################################################
   def Get_SW_SPDT(self,slot=11,sw=1):
      # ROUT:CLOS? (@F01A11(0161))
      outstr = 'ROUT:CLOS? (@F01A%02d(01%02d))'%(slot,sw)
      print(outstr)
      #self.queryFloat(outstr)
      return out 

   def Get_SW_SP6T(self,slot=11,sw=1):
      # ROUT:CLOS? (@F01A11(0161))
      for pos in range(0,7):
         outstr = 'ROUT:CLOS? (@F01A%02d(%02d%02d))'%(slot,pos,sw)
         state = self.queryInt(outstr)[0]
         if state == 1:
            CurrState = pos
            print("We are at %d"%pos)
      return CurrState
         

   def Set_SW(self,slot=11,sw=1,pos=1):
      # ROUT:CLOS (@F01A11(0161))
      outstr = 'ROUT:CLOS (@F01A%02d(%02d%02d))'%(slot,pos,sw)
      print(outstr)
      self.write(outstr)

#####################################################################
### Run if Main
#####################################################################
if __name__ == "__main__":
   ### this won't be run when imported
   RFU3 = OSP()
   RFU3.jav_openvisa('TCPIP0::192.168.1.150::INSTR')
   RFU3.Set_SW(12,61,6)
   RFU3.Get_SW_SP6T(12,61)
   RFU3.jav_ClrErr()
