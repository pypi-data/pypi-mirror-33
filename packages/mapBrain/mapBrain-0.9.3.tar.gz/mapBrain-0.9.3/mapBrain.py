#!/usr/bin/env python

import numpy
from scipy.stats import kurtosis, skew

class SphericalBrainMapping(object):
    """ 
    Performs a Spherical Brain Mapping of a 3D Brain Image 
    
    :param resolution: Angle resolution at which each mapping vector is computed (default 1 degree)
    :type resolution: int, float
    :param deformation: Rate of unequally distributed mapping vectors, to be used when the surface to be mapped is not spherical but ellipsoid (in the range 0-1, with 0 meaning a perfect sphere)
    :type deformation: float 
    :param ithreshold: Intensity threshold (:math:`I_{th}`) for the projections needing it (default 0)
    :type ithreshold: float
    :param nlayers: Nummber of equally distributed layers (default 1)
    :type nlayers: int
    """
    
    def __init__(self, resolution=1, deformation=0.0, ithreshold=0, nlayers=1):
        """
        Initializes a SBM instance, saving all parameters as attributes of the 
        instance. 
        
        :param resolution: Angle resolution at which each mapping vector is computed (default 1 degree)
        :type resolution: int, float
        :param deformation: Rate of unequally distributed mapping vectors, to be used when the surface to be mapped is not spherical but ellipsoid (in the range 0-1, with 0 meaning a perfect sphere)
        :type deformation: float 
        :param ithreshold: Intensity threshold (:math:`I_{th}`) for the projections needing it (default 0)
        :type ithreshold: float
        :param nlayers: Nummber of equally distributed layers (default 1)
        :type nlayers: int
        """
        self.resolution = resolution
        self.deformation = deformation
        self.ithreshold = ithreshold
        self.nlayers = nlayers
        
    def vsetResolution(self, resolution=1):
        """ 
        Sets the angular resolution at which the map will be computed
        
        :param resolution: Angle resolution at which each mapping vector is computed (default 1 degree)
        :type resolution: int, float
        """
        self.resolution = resolution
        
    def vsetDeformation(self, deformation=0.0):
        """ 
        Sets the deformation rate to be used in SBM. 
        
        :param deformation: Rate of unequally distributed mapping vectors, to be used when the surface to be mapped is not spherical but ellipsoid (in the range 0-1, with 0 meaning a perfect sphere)
        :type deformation: float 
        """
        self.deformation = deformation
        
    def vsetIThreshold(self, ithreshold=0):
        """ 
        Sets the intensity threshold to be used in SBM.
        
        :param ithreshold: Intensity threshold ($I_{th}$) for the projections needing it (default 0)
        :type ithreshold: float
        """
        self.ithreshold = ithreshold
    
    def vsetNLayers(self, nlayers=1):
        """
        Sets the number of layers to be mapped
        
        :param nlayers: Nummber of equally distributed layers (default 1)
        :type nlayers: int
        """
        self.nlayers = nlayers
        
    def getResolution(self):
        """ Returns the resolution used in SBM. """
        return self.resolution
    
    def getDeformation(self):
        """ Returns the current deformation rate used in SBM """
        return self.deformation
        
    def getIThreshold(self):
        """ Returns the Intensity Threshold used in SBM """
        return self.ithreshold
        
    def getNLayers(self):
        """ Returns the number of layers used in SBM """
        return self.nlayers
        
    def computeMappingVectors(self):
        """ Computes the mapping vectors azim and elev
        """
        spaceVector = 1 - self.deformation*numpy.cos(numpy.deg2rad(numpy.arange(-2*180,2*180+self.resolution,self.resolution*2)))
        azim = numpy.deg2rad(numpy.cumsum(spaceVector)*self.resolution-270)
        elev = numpy.deg2rad(numpy.arange(-90, 90+self.resolution, self.resolution))
        return azim, elev
        
    def surface(self, vset):
        """ Returns the surface of all mapped voxels
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        val = numpy.argwhere(vset>self.ithreshold)
        if len(val)==0:
            val=numpy.zeros(1)
        return numpy.nanmax(val)
        
    def thickness(self, vset):
        """ Returns the thickness of the layer of mapped voxels
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        aux = numpy.argwhere(vset>self.ithreshold)
        if aux.size>0:
            thickness = numpy.nanmax(aux) - numpy.nanmin(aux)
        else:
            thickness = 0
        return thickness
        
    def numfold(self, vset):
        """ Returns the number of non-connected subvsets in the mapped voxels
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        return numpy.ceil(len(numpy.argwhere(numpy.bitwise_xor(vset[:-1]>self.ithreshold, vset[1:]>self.ithreshold)))/2.)
        
    def average(self, vset):
        """ Returns the average of the sampling vset
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        return numpy.nanmean(vset)     
           
    def variance(self, vset):
        """ Returns the variance of the sampling vset
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        return numpy.nanvar(vset)      
           
    def skewness(self, vset):
        """ Returns the skewness of the sampling vset
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        return skew(vset, bias=False)
           
    def entropy(self, vset):
        """ Returns the entropy of the sampling vset
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        return sum(numpy.multiply(vset[vset>self.ithreshold],numpy.log(vset[vset>self.ithreshold])))
           
    def kurtosis(self, vset):
        """ Returns the kurtosis of the sampling vset
        
        :param vset: set of mapped voxels' intensity
        :type vset: 1-dimensional numpy array
        """
        return kurtosis(vset, fisher=False, bias=False)        


    def _interp_single_gray_level(self, p, imag):
        ''' Interpolates the gray level found at the point p
        using interpolation by percentage of superposition of
        pixels.
        
        ''' 
        # We create the array of surrounding points: 
        a = numpy.array([[0, 0, 0],
                      [0, 0, 1],
                      [0, 1, 0],
                      [0, 1, 1],
                      [1, 0, 0],
                      [1, 0, 1],
                      [1, 1, 0],
                      [1, 1, 1]])
        points = (numpy.floor(p)+a).astype(int)
        
        # Extract the colours at each point:
        c = imag[points[:,0], points[:,1], points[:,2]]
        
        # Calculate the weights as distances:
        w = numpy.prod(1-numpy.abs(p-points),axis=1)
        
        # And sum the different values: 
        ci = numpy.sum(c*w)
        return ci
    
    def _interp_gray_level(self, p, imag):
        ''' Interpolates the gray level found at the point array p
        by using superposition interpolation. 
        ''' 
        if p.ndim==3:
            ci = numpy.zeros(p.shape[:2])
            for i in range(p.shape[0]):
                ci[i,:] = numpy.array([self._interp_single_gray_level(punto,imag) for punto in p[i,:,:]])
                
        elif p.ndim==2:
            ci = numpy.array([self._interp_single_gray_level(punto,imag) for punto in p])
        return ci


    def _get_points_centering(self, center, n):
        ''' 
        Gets the array of centerpoints in a given 
        direction (n), in this order:
        -------------
        | 1 | 2 | 3 |
        |------------
        | 8 | 0 | 4 |
        |-----------|
        | 7 | 6 | 5 |
        -------------
        
        :param center: Specifies the position of the origin of mapping vectors. If not specified, defaults to the geometrical center of the image. 
        :type center: 3D coordinates in numpy array
        :param n: normal vector specifying the direction
        :type n: 3D coordinates in numpy array
            
        '''
        u11 = numpy.sqrt(n[1]**2/(n[0]**2+n[1]**2))
        u12 = -numpy.sqrt(n[1]**2/(n[0]**2+n[1]**2))
        u21 = numpy.sqrt(1-u11**2)
        u22 = numpy.sqrt(1-u12**2)
        
        u1 = numpy.array([u11, u21, 0])
        u2 = numpy.array([u12, u22, 0])
        
        if numpy.dot(u1,n)<1e-10:
            u = u1
        else:
            u = u2
        
        v = numpy.cross(n,u)
        
        p0 = center
        p1 = center - u + v
        p2 = center + v
        p3 = center + u + v
        p4 = center + u
        p5 = center + u - v
        p6 = center - v
        p7 = center - u - v
        p8 = center - u
        return numpy.array([p0, p1, p2, p3, p4, p5, p6, p7, p8])
    
    def _posterizeImage(self, ndarray, numLevels = 16 ):
        ''' 
        Posterizes the image to number of levels
        '''
        
        #Gray-level resizing
        numLevels = numLevels-1 #don't touch. Logical adding issue.
        minImage = numpy.nanmin(ndarray)
        ndarray = ndarray-(minImage)
        maxImage = numpy.nanmax(ndarray)
        tempShift = maxImage/numLevels
        ndarray = numpy.floor(ndarray/tempShift)
        ndarray=ndarray + 1
        numLevels = numLevels + 1 # don't touch. Logical adding issue.
        
        return ndarray


    def computeTexture(self, p, imag, origin, distances=1):
        '''
        Computes the texture around vector p
        
        :param p: The mapping or rojecting vector :math:`\mathbf{v}_{{\\theta},{\\varphi}}`
        :param imag: Three-dimensional intensity array corresponding to a 3D registered brain image. 
        :type imag: 3D numpy array
        :param origin: Specifies the position of the origin of mapping vectors. If not specified, defaults to the geometrical center of the image. 
        :type origin: 3D coordinates in numpy array
        :param distances: It helds the distances at which the GLCM is going to be computed. 
        :type distances: integer or list of integers
        '''
        from mahotas.features import texture
        
        # set the originso of each vector (the central one and surrounding 8)
        origins = self._get_points_centering(origin, p[1,:])
        puntos = numpy.array([p+cent for cent in origins])
        select = (puntos<numpy.array(imag.shape)-1).all(axis=2).all(axis=0)
        p_real = puntos[:,select,:]
        
        colors = self._interp_gray_level(p_real, imag)
        
        ndarray = self._posterizeImage(colors)
        
        # Prevent errors with iterative list, adding support for 
        # several distances in the computation of the GLCM
        if (type(distances) is not list) and (type(distances) is not numpy.ndarray):
            distances = [distances]        
        
        glcm=[]
        for dis in distances:
            glcm.append(texture.cooccurence(ndarray.astype(int)-1, 0, distance=dis, symmetric=False))
        features = texture.haralick_features(glcm)
        labels = texture.haralick_labels
        return features, labels
    
    
    def showMap(self, map, measure, cmap='gray'):
        """ Shows the computed maps in a window using pyplot
        
        :param map: map or array of maps to be shown
        :type map: numpy ndarray
        :param measure: SBM measure to be computed
        :type measure: string
        :param cmap: Colormap to use in representation
        :type cmap: string with valid matplotlib colormap
        """
        import matplotlib.pyplot as plt
        # Set the maximum and minimum value of the computed maps
        minimum = numpy.min(map)
        maximum = numpy.max(map)
        if self.nlayers>1:
            imgplot = plt.figure()
            # Trick for plotting large numbers of layers in a kept proportion
            ncol = numpy.floor(self.nlayers/numpy.ceil(self.nlayers**(1.0/3)))
            nrow = numpy.ceil(self.nlayers/ncol)
            for nl in range(self.nlayers):
                plt.subplot(nrow,ncol,nl+1)
                plt.imshow(numpy.rot90(map[nl]),cmap=cmap, vmin=minimum, vmax=maximum)
                plt.title(measure+'-SBM ('+str(nl)+')')
                plt.colorbar()
            plt.show()
        elif measure=='texture':
            # If texture, it plots 13 as if they were layers.
            imgplot = plt.figure()
            ncol = numpy.floor(13/numpy.ceil(13**(1.0/3)))
            nrow = numpy.ceil(13/ncol)
            for nl in range(13):
                plt.subplot(nrow,ncol,nl+1)
                plt.imshow(numpy.rot90(map[nl,:,:]),cmap=cmap, vmin=minimum, vmax=maximum)
                plt.title(measure+'-SBM ('+str(nl)+')')
                plt.colorbar()
            plt.show()
                
        else:
            imgplot = plt.figure()
            plt.imshow(numpy.rot90(map[0]),cmap=cmap, vmin=minimum, vmax=maximum)
            plt.title(measure+'-SBM')
            plt.colorbar()
            plt.show()
        
        return imgplot
                
            
            
    def sph2cart(self, theta, phi, r):
        """ Returns the corresponding spherical coordinates given the elevation,
        azimuth and radius
        
        :param theta: Azimuth angle (radians)
        :type theta: float
        :param phi: Elevation angle (radians)
        :type phi: float
        :param rad: Radius 
        :type rad: float
        """
        z = r * numpy.sin(phi)
        rcosphi = r * numpy.cos(phi)
        x = rcosphi * numpy.cos(theta)
        y = rcosphi * numpy.sin(theta)
        return x, y, z

            
    def doSBM(self, image, measure='average', show=True, origin=None):
        """ 
        Performs the SBM on the selected image and using the specified measure
        
        :param image: Three-dimensional intensity array corresponding to a 3D registered brain image. 
        :type image: 3D numpy array
        :param measure: SBM measure to be computed
        :type measure: string
        :param show: Specifies whether to show the computed map (True) or not (False)
        :type show: bool
        :param origin: Specifies the position of the origin of mapping vectors. If not specified, defaults to the geometrical center of the image. 
        :type origin: 3D coordinates in numpy array
        """
        image[numpy.isnan(image)] = 0
        tam = image.shape                           # Size of the image
        if origin is None:
            origin = numpy.divide(image.shape,2)    # To compute the middle point
        lon = max(origin)                       # Compute the maximum value of the mapping vector v
#        tamArr=numpy.repeat([tam],lon,0) # Residual

        # We create the mapping vectors and perform the conversion from spherical
        # coordinates to cartesian coordiantes (the ones in our 3D array). 
        azim, elev = self.computeMappingVectors()
        THETA,PHI,RAD = numpy.meshgrid(azim, elev, numpy.arange(lon))
        x,y,z = self.sph2cart(THETA,PHI,RAD)
        
        if measure=='texture':
            # Define the blank map to be filled (nlayers, features, 361, 181)
            mapa = numpy.zeros([13, numpy.ceil(361/self.resolution).astype(int), numpy.ceil(181/self.resolution).astype(int)])
#            for nl in range(self.nlayers):
#                intvl=numpy.int32(numpy.floor(lon/self.nlayers)) # no sirve para nada todavía
            # eliminamos el número de capas
            for i in range(azim.shape[0]):
                for j in range(elev.shape[0]):
                    p = numpy.vstack((x[j,i,:].flatten(),y[j,i,:].flatten(),z[j,i,:].flatten())).T
                    mapa[:,i,j], _ = self.computeTexture(p, image, origin)
            
        else:
            X = numpy.int32(numpy.round(x+origin[0]))
            Y = numpy.int32(numpy.round(y+origin[1]))
            Z = numpy.int32(numpy.round(z+origin[2]))
            coord = numpy.ravel_multi_index((X,Y,Z), mode='clip', dims=tam, order='F').transpose((1,0,2))
    
            # This is the blank map to be filled. 
            mapa = numpy.zeros([self.nlayers, numpy.ceil(361/self.resolution).astype(int), numpy.ceil(181/self.resolution).astype(int)])
            
            # Begin of the loop
            image = image.flatten('F')
            for nl in range(self.nlayers):
                intvl=numpy.int32(numpy.floor(lon/self.nlayers))
                for i in range(coord.shape[0]):
                    for j in range(coord.shape[1]):
                        vset = numpy.squeeze(image[coord[i][j][nl*intvl:(nl+1)*intvl]])
                        if measure.__class__==type('str'):
                            try:
                                mapa[nl][i][j] = getattr(self,measure)(vset)
                            except AttributeError:
                                print("The measure %s is not supported"%measure)
                                return
                            
        # If it has been vset, we display the map
        if show:
            self.showMap(mapa,measure)

        return mapa
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
