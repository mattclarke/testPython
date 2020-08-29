# channelToImageAD.py

import numpy as np
import math


class ChannelToImageAD() :
    '''
channelToImageAD provides python access to the data provided by areaDetector/ADSupport
It is meant for use by a callback from an NTNDArray record.
NTNDArray is implemented in areaDetector/ADCore.
NTNDArray has the following fields of interest to ChannelToImageAD:
    value            This contains a numpy array with a scalar dtype
    dimension        2d or 3d array description
      
Normal use is:
...
from channelToImageAD import ChannelToImageAD
...
    self.channelToImageAD = ChannelToImageAD()
    self.channelDict = self.channelToImage.channelDictCreate()
    
...
    try:
        self.channelToImage.channelToImage(data,dimArray,self.imageSize,...)
        channelDict = self.channelToImage.getImageDict()
        self.channelDict["image"] = channelDict["image"]
        ... other methods
...   
     
Copyright - See the COPYRIGHT that is included with this distribution.
    NTNDA_Viewer is distributed subject to a Software License Agreement found
    in file LICENSE that is included with this distribution.

authors
    Marty Kraimer
    Mark Rivers
latest date 2020.07.30
    '''
    def __init__(self,parent=None) :
        self.__image = None
        self.__channelDict = self.channelDictCreate()
        self.__channelLimits = (0,255)
        self.__imageLimits = (0,255)
        self.__manualLimits = (0,255)

    def channelDictCreate(self) :
        """
        Returns
        -------
        channelDict : dict
            channelDict["channel"]      None
            channelDict["dtypeChannel"] None
            channelDict["nx"]           0
            channelDict["ny"]           0
            channelDict["nz"]           0
            channelDict["image"]        None
            channelDict["dtypeImage"]   np.uint8
            channelDict["compress"]     1
        """
        return {\
             "channel" : None ,
             "dtypeChannel" : None ,
             "dtypeImage" : np.uint8  ,
             "nx" : 0 ,
             "ny" : 0 ,
              "nz" : 0,
              "image" : None ,
              "dtypeImage" : np.uint8  ,
              "compress" : 1 }

    def setManualLimits(self,manualLimits) :
        """
         Parameters
        -----------
            manualLimits : tuple
                 manualLimits[0] : lowManualLimit
                 manualLimits[1] : highManualLimit
        """
        self.__manualLimits = manualLimits

    def getChannelDict(self) :
        """ 
        Returns
        -------
        channelDict : dict
            channelDict["channel"]      numpy 2d or 3d array for the channel
            channelDict["dtypeChannel"] dtype for data from the callback
            channelDict["nx"]           nx for data from the callback
            channelDict["ny"]           ny for data from the callback
            channelDict["nz"]           nz (1,3) for (2d,3d) image
            channelDict["imagel"]       numpy 2d or 3d array for the image
            channelDict["dtypeImage"]   dtype for image
            channelDict["compress"]     how much channel data was compressed 
        
        """
        return self.__channelDict
 
    def getChannelLimits(self) :
        """ 
        Returns
        -------
        channelLimits : tuple
            channelLimits[0]    lowest value of data from the callback
            channelLimits[0]    highest value of data from the callback
        
        """
        return self.__channelLimits

    def getImageLimits(self) :
        """ 
        Returns
        -------
        imageLimits : tuple
            imageLimits[0]    lowest value of data from the image
            imageLimits[0]    highest value of data from the image
        
        """
        return self.__imageLimits

    def getManualLimits(self) :
        """
        Returns
        -------
            manualLimits : tuple
                 manualLimits[0] : lowManualLimit
                 manualLimits[1] : highManualLimit
        """
        return self.__manualLimits

    def reshape(self,data,dimArray,compress=1) :
        """
         Parameters
        -----------
            data     : data from the callback
            dimArray : dimension from callback
        """
        nz = 1
        ndim = len(dimArray)
        if ndim ==2 :
            nx = dimArray[0]["size"]
            ny = dimArray[1]["size"]
            if compress!=1 :
                nx = int(nx/compress)
                ny = int(ny/compress)
            image = np.reshape(data,(ny,nx))
        elif ndim ==3 :
            if dimArray[0]["size"]==3 :
                nz = dimArray[0]["size"]
                nx = dimArray[1]["size"]
                ny = dimArray[2]["size"]
                if compress!=1 :
                    nx = int(nx/compress)
                    ny = int(ny/compress)
                image = np.reshape(data,(ny,nx,nz))
            elif dimArray[1]["size"]==3 :
                nz = dimArray[1]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[2]["size"]
                if compress!=1 :
                    nx = int(nx/compress)
                    ny = int(ny/compress)
                image = np.reshape(data,(ny,nz,nx))
                image = np.swapaxes(image,2,1)
            elif dimArray[2]["size"]==3 :
                nz = dimArray[2]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[1]["size"]
                if compress!=1 :
                    nx = int(nx/compress)
                    ny = int(ny/compress)
                image = np.reshape(data,(nz,ny,nx))
                image = np.swapaxes(image,0,2)
                image = np.swapaxes(image,0,1)
            else  :  
                raise Exception('no axis has dim = 3')
                return
        else :
                raise Exception('ndim not 2 or 3')
        return (image,nx,ny,nz)        
        
    def channelToImage(self,data,dimArray,imageSize,manualLimits=False,showLimits=False) :
        """
         Parameters
        -----------
            data               : data from the callback
            dimArray           : dimension from callback
            imageSize          : width and height for the generated image
            manualLimits       : (False,True) means client (does not,does) set limits
            showLimits         : (False,True) means channelLimits and imageLimits (are not, are) updated
        """
        dtype = data.dtype
        reshape = self.reshape(data,dimArray)
        self.__channelDict["channel"] = reshape[0]
        self.__channelDict["nx"] = reshape[1]
        self.__channelDict["ny"] = reshape[2]
        self.__channelDict["nz"] = reshape[3]
        self.__channelDict["dtypeChannel"] = dtype
        if dtype==np.uint8 and not manualLimits :
            dataMin = 0
            dataMax =255
        else:
            if dtype != np.uint8 :
                dataMin = np.min(data)
                dataMax = np.max(data)
            else :
                dataMin = 0
                dataMax =255
            if  manualLimits :
                displayMin = self.__manualLimits[0]
                displayMax = self.__manualLimits[1]
            else :  
                displayMin = dataMin
                displayMax = dataMax
            xp = (displayMin, displayMax)
            fp = (0.0, 255.0)
            data = (np.interp(data,xp,fp)).astype(np.uint8)
        if showLimits :
            self.__channelLimits = (dataMin,dataMax) 
            imageMin = np.min(data)
            imageMax = np.max(data)
            self.__imageLimits = (imageMin,imageMax)
        retval = self.reshape(data,dimArray)
        image = retval[0]
        nx = retval[1]
        ny = retval[2]
        nz = retval[3]
        nmax = 0
        if nx>nmax : nmax = nx
        if ny>nmax : nmax = ny
        compress = 1
        if nmax > imageSize :
            compress = math.ceil(float(nmax)/imageSize)
            if nz==1 :
                image = image[::compress,::compress]
            else :
                image =  image[::compress,::compress,::]
        reshape = self.reshape(image,dimArray,compress=compress)     
        self.__channelDict["image"] = image        
        self.__channelDict["compress"] = compress
        
