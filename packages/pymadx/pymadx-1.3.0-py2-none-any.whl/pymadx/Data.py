"""
Classes to load and manipulate data from MADX.
"""

import bisect as _bisect
import copy as _copy
import gzip as _gzip
import numpy as _np
import re as _re
import string as _string
import tarfile
import os.path

from _General import GetSixTrackAperType as _GetSixTrackAperType
from _General import Cast as _Cast

class Tfs(object):
    """
    MADX Tfs file reader

    >>> a = Tfs()
    >>> a.Load('myfile.tfs')
    >>> a.Load('myfile.tar.gz') -> extracts from tar file

    or

    >>> a = Tfs("myfile.tfs")
    >>> b = Tfs("myfile.tar.gz")

    | `a` has data members:
    | header      - dictionary of header items
    | columns     - list of column names
    | formats     - list of format strings for each column
    | data        - dictionary of entries in tfs file by name string
    | sequence    - list of names in the order they appear in the file
    | nitems      - number of items in sequence

    NOTE: if no column "NAME" is found, integer indices are used instead

    See the various methods inside a to get different bits of information:

    >>> a.ReportPopulations?

    Examples:

    >>> a.['IP.1'] #returns dict for element named "IP.1"
    >>> a[:30]     #returns list of dicts for elements up to number 30
    >>> a[345]     #returns dict for element number 345 in sequence

    """
    # The Tfs class data model:
    # The NAME column for a given row refers to the name of the
    # accelerator component.  Each row is stored in a dictionary,
    # self.data, with the mangled NAME as a key, and the row as the
    # entry.  The names must be mangled as they are in general not
    # unique.  Dictionaries are not ordered, so the sequence of these
    # mangled names is stored in self.sequence.  Two accelerator
    # components with identical names in the sequence will be
    # identical, but the optical functions at that point will in
    # general be different.
    def __init__(self,filename=None,**kwargs):
        object.__init__(self) #this allows type comparison for this class
        self.index       = []
        self.header      = {}
        self.columns     = []
        self.formats     = []
        self.data        = {}
        self.sequence    = []
        self.nitems      = 0
        self.nsegments   = 0
        self.segments    = []
        self.filename    = filename
        self.smax        = 0
        self.smin        = 0
        self.ptctwiss    = False # whether data was generated via ptctwiss
        self._verbose    = False
        if 'verbose' in kwargs:
            self._verbose = kwargs['verbose']
        self._calculatessigma = True
        if 'calculatesigma' in kwargs:
            self._calculatessigma = kwargs['calculatesigma']
        if type(filename) == str:
            self.Load(filename, self._verbose)
        elif type(filename) == Tfs:
            self._DeepCopy(filename)

    def Clear(self):
        """
        Empties all data structures in this instance.
        """
        self.__init__()

    def Load(self, filename, verbose=False):
        """
        >>> a = Tfs()
        >>> a.Load('filename.tfs')

        Read the tfs file and prepare data structures. If 'tar' or 'gz are in
        the filename, the file will be opened still compressed.
        """
        if tarfile.is_tarfile(filename): # assume compressed tarball of 1 file
            print 'pymadx.Tfs.Load> zipped file'
            tar = tarfile.open(filename, 'r')
            f = tar.extractfile(tar.getmember(tar.getnames()[-1])) # extract the last member
        elif filename.endswith('.gz'): # gzipped file
            print 'pymadx.Tfs.Load> zipped file'
            f = _gzip.open(filename, 'r')
        else:
            print 'pymadx.Tfs.Load> normal file'
            f = open(filename, 'r')

        #first pass at file - need to check if it has 'NAME' column
        #if it has name, use that, otherwise use an integer
        #find column names line
        for line in f:
            if not line.strip():
                continue #protection against empty lines being misidentified as column lines
            sl = line.strip('\n').split()
            if line[0] == '*':
                #name
                self.columns.extend(sl[1:]) #miss "*" from column names line
                if verbose:
                    print 'Columns will be:'
                    print self.columns
                break
        if 'NAME' in self.columns:
            usename = True #use the name
        else:
            usename = False #no name column - use an index
        self.columns =  [] #reset columns for proper data read in
        f.seek(0) #reset file back to the beginning for reading in data

        #segment specific stuff
        segment_i = 0 #actual segment number in data may not be zero counting - use this variable
        segment_name = 'NA'
        #always include segments - put as first column in data
        self.columns.append("SEGMENT")
        self.formats.append("%d")
        self.columns.append("SEGMENTNAME")
        self.formats.append("%s")

        namecolumnindex = 0

        def CastAndStrip(arg):
            argCast = _Cast(arg)
            if type(argCast) == str:
                #print argCast
                argCast = argCast.strip('"') # strip unnecessary quote marks off
                #print argCast
            return argCast

        #read in data
        for line in f:
            if not line.strip():
                continue #protect against empty lines, although they should not exist
            splitline = line.strip('\n').split()
            sl        = splitline #shortcut
            if line[0] == '@':
                # Header
                self.header[sl[1]] = CastAndStrip(sl[-1])
            elif line[0] == '*':
                #name
                self.columns.extend(sl[1:]) #miss *
                if "NAME" in self.columns:
                    namecolumnindex = self.columns.index("NAME")
            elif line[0] == '$':
                #format
                self.formats.extend(sl[1:]) #miss $
            elif '#' in line[0]:
                #segment line
                d = [CastAndStrip(item) for item in sl[1:]]
                segment_i    = d[0]
                segment_name = d[-1]
                self.nsegments += 1 # keep tally of number of segments
                self.segments.append(segment_name)
            else:
                #data
                d = [CastAndStrip(item) for item in sl]
                d.insert(0,segment_name) #prepend segment info
                d.insert(0,segment_i) #this one becomes the first item matching the column index
                if usename:
                    name = self._CheckName(d[namecolumnindex])
                else:
                    name = self.nitems
                self.sequence.append(name) # keep the name in sequence
                self.data[name] = d        # put in data dict by name
                self.nitems += 1           # keep tally of number of items

        f.close()

        try:
            self.ptctwiss = self.header['NAME'] == "PTC_TWISS"
        except KeyError:
            pass # no name key in header

        #additional processing
        self.index = range(0,len(self.data),1)
        if 'S' in self.columns:
            self.smin = self[0]['S']
            self.smax = self[-1]['S']
            sindex = self.ColumnIndex('S')
            sEnd = self.GetColumn('S')  #calculating the mid points as the element
            sEnd = _np.insert(sEnd,0,0)
            sMid = (sEnd[:-1] + sEnd[1:])/2

            for i, name in enumerate(self.sequence):
                self.data[name].append(self.data[name][sindex]) # copy S to SORIGINAL
                self.data[name].append(sMid[i])
                self.data[name].append(name)
            self.columns.append('SORIGINAL')
            self.formats.append('%le')
            self.columns.append('SMID')
            self.formats.append('%le')
            # Additional column which is just the name used to define
            # the sequence in self.sequence.
            self.columns.append("UNIQUENAME")
            self.formats.append("%s")
            assert len(set(self.GetColumn("UNIQUENAME"))) == len(self)

        else:
            self.smax = 0

        #Check to see if input Tfs is Sixtrack style (i.e no APERTYPE, and is instead implicit)
        if 'APER_1' in self.columns and 'APERTYPE' not in self.columns:
            self.columns.append('APERTYPE')
            self.formats.append('%s')

            for key, element in self.data.iteritems():
                aper1 = element[self.columns.index('APER_1')]
                aper2 = element[self.columns.index('APER_2')]
                aper3 = element[self.columns.index('APER_3')]
                aper4 = element[self.columns.index('APER_4')]
                apertype = _GetSixTrackAperType(aper1,aper2,aper3,aper4)

                element.append(apertype)

        if self._calculatessigma:
            self._CalculateSigma()
        self.names = self.columns

    def _CalculateSigma(self):
        # check for emittance and energy spread
        ex   = 1e-9
        ey   = 1e-9
        sige = 1e-4
        requiredVariablesH1 = set(['SIGE', 'EX', 'EY'])
        method1 = requiredVariablesH1.issubset(self.header.keys())
        requiredVariablesH2 = set(['EXN', 'EYN', 'GAMMA'])
        method2 = requiredVariablesH2.issubset(self.header.keys())
        if not (method1 or method2):
            return #no emittance information to calculate sigma

        def getColumnIndex(opticalFuncNames):
            madxName = opticalFuncNames[0]
            ptcName  = opticalFuncNames[1]

            # return index of madx or ptc variable
            if madxName in self.columns:
                return self.ColumnIndex(madxName)
            elif ptcName in self.columns:
                # if the equivalent madx named column does not already exist
                # append it to the instance and update with the correct data
                if not madxName in self.columns:
                    self.formats.extend(['%le'])
                    self.columns.extend([madxName])
                    ptcIndex = self.ColumnIndex(ptcName)
                    for elementname in self.sequence:
                        d = self.data[elementname]
                        d.append(d[ptcIndex])
                # return the original PTC column
                return self.ColumnIndex(ptcName)
            else:
                print("Columns "+madxName+" and "+ptcName+" missing from tfs file")
                return None

        # optical function list format:
        # [madxVariableName,  ptcVariableName]
        betxColumn = ['BETX', 'BETA11']
        betyColumn = ['BETY', 'BETA22']
        alfxColumn = ['ALFX', 'ALFA11']
        alfyColumn = ['ALFY', 'ALFA22']
        dxColumn   = ['DX',   'DISP1']
        dyColumn   = ['DY',   'DISP3']
        dpxColumn  = ['DPX',  'DISP2']
        dpyColumn  = ['DPY',  'DISP4']

        # get indices to the columns we'll need in the data
        betxindex = getColumnIndex(betxColumn)
        betyindex = getColumnIndex(betyColumn)
        alfxindex = getColumnIndex(alfxColumn)
        alfyindex = getColumnIndex(alfyColumn)
        dxindex   = getColumnIndex(dxColumn)
        dyindex   = getColumnIndex(dyColumn)
        dpxindex  = getColumnIndex(dpxColumn)
        dpyindex  = getColumnIndex(dpyColumn)

        # lists of all required variables for the sigma calculations
        spaceColumns = [betxindex, betyindex, dxindex, dyindex]
        primeColumns = [betxindex, betyindex, alfxindex, alfyindex, dpxindex, dpyindex]

        calculateSpace = True
        calculatePrime = True
        if None in spaceColumns:
            calculateSpace = False
        if None in primeColumns:
            calculatePrime = False

        if not (calculateSpace or calculatePrime):
            return # can't calculate either

        # constants
        if 'GAMMA' not in self.header:
            self.header['BETA'] = 1.0 # assume super relativistic
        else:
            self.header['BETA'] = _np.sqrt(1.0 - (1.0/(self.header['GAMMA']**2)))
        beta = self.header['BETA'] # relativistic beta
        if method1:
            ex   = self.header['EX']
            ey   = self.header['EY']
            sige = self.header['SIGE']
        if method2:
            ex   = self.header['EXN']*self.header['GAMMA']
            ey   = self.header['EYN']*self.header['GAMMA']
            sige = 0

        # for extending TFS beyond madx supplied columns if necessary
        newcolumns = []

        # extend class with columns of (beta * dispersion) to match madx at low energy
        # also extend for beam sizes
        if calculateSpace:
            newcolumns.extend(['DXBETA', 'DYBETA', 'SIGMAX', 'SIGMAY'])
            self.formats.extend(['%le','%le','%le','%le'])
        if calculatePrime:
            newcolumns.extend(['DPXBETA', 'DPYBETA', 'SIGMAXP', 'SIGMAYP'])
            self.formats.extend(['%le','%le','%le','%le'])
        self.columns.extend(newcolumns)

        for elementname in self.sequence:
            # beam size calculations (using relation deltaE/E = beta^2 * deltaP/P)
            d = self.data[elementname]
            if calculateSpace:
                if self.ptctwiss:
                    dxbeta = d[dxindex]
                    dybeta = d[dyindex]
                else:
                    dxbeta = d[dxindex]*beta
                    dybeta = d[dyindex]*beta
                xdispersionterm = (dxbeta * sige / beta**2)**2
                ydispersionterm = (dybeta * sige / beta**2)**2
                sigx = _np.sqrt((d[betxindex] * ex) + xdispersionterm)
                sigy = _np.sqrt((d[betyindex] * ey) + ydispersionterm)
                # append in the same order that the columns were extended above
                d.append(dxbeta)
                d.append(dybeta)
                d.append(sigx)
                d.append(sigy)

            # beam divergences (using relation x',y' = sqrt(gamma_x,y * emittance_x,y))
            if calculatePrime:
                gammax = (1.0 + d[alfxindex]**2) / d[betxindex] # twiss gamma
                gammay = (1.0 + d[alfyindex]**2) / d[betyindex]
                if self.ptctwiss:
                    dpxbeta = d[dpxindex]
                    dpybeta = d[dpyindex]
                else:
                    dpxbeta = d[dpxindex]*beta
                    dpybeta = d[dpyindex]*beta
                xdispersionterm = (dpxbeta * sige / beta**2)**2
                ydispersionterm = (dpybeta * sige / beta**2)**2
                sigxp  = _np.sqrt((gammax * ex) + xdispersionterm)
                sigyp  = _np.sqrt((gammay * ey) + ydispersionterm)
                # append in the same order that the columns were extended above
                d.append(dpxbeta)
                d.append(dpybeta)
                d.append(sigxp)
                d.append(sigyp)

    def __repr__(self):
        if self.filename is not None:
            return "<pymadx.Data.Tfs, {} items in lattice ({})>".format(
                self.nitems,
                os.path.basename(self.filename))
        return "<pymadx.Data.Tfs, {} items in lattice>".format(self.nitems)

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        self._iterindex = -1
        return self

    def next(self):
        if self._iterindex == len(self.sequence)-1:
            raise StopIteration
        self._iterindex += 1
        return self.GetRowDict(self.sequence[self._iterindex])

    def __contains__(self, name):
        return name in self.GetColumn("NAME")

    def __getitem__(self,index):
        #index can be a slice object, string or integer - deal with in this order
        #return single item or slice of lattice
        if type(index) == slice:
            start,stop,step = index.start, index.stop, index.step #note slices are immutable
            if step is not None and step < 0:
                raise ValueError("Negative steps are not supported.")
            #test values incase of ':' use
            if step != None and type(step) != int:
                raise ValueError("Invalid step "+step)
            if start != None and stop != None and step != None:
                # [start:stop:step]
                start = self._EnsureItsAnIndex(start)
                stop  = self._EnsureItsAnIndex(stop)
            elif start != None and stop != None and step == None:
                # [start:stop]
                start = self._EnsureItsAnIndex(start)
                stop  = self._EnsureItsAnIndex(stop)
                step  = 1
            elif start == None and stop == None and step > 0:
                # [::step]
                start = 0
                stop  = len(self)
            elif start != None and stop == None and step > 0:
                # [start::step]
                start = self._EnsureItsAnIndex(start)
                stop  = len(self)
            elif start != None and stop == None and step == None:
                # [start::]
                start = self._EnsureItsAnIndex(start)
                stop  = len(self)
                step  = 1
            elif start == None and stop != None and step > 0:
                # [:stop:step]
                start = 0
                stop  = self._EnsureItsAnIndex(stop)
            elif start == None and stop != None and step == None:
                # [:stop]
                start = 0
                stop  = self._EnsureItsAnIndex(stop)
                step  = 1
            index = slice(start,stop,step)
            #construct and return a new instance of the class
            a = Tfs()
            a._CopyMetaData(self)

            # whether to prepare new s coordinates as extra entry
            prepareNewS = False
            sOffset     = 0
            if start > 0 and 'S' in self.columns:
                prepareNewS = True
                # if 'S' is in the columns, 'SORIGINAL' will be too
                sStart = self.GetRowDict(self.sequence[start-1])['S']
                if stop==len(self):
                    #Zero counted, make sure stop index not outside of range
                    sEnd   = self.GetRowDict(self.sequence[stop-1])['S']
                else:
                    sEnd   = self.GetRowDict(self.sequence[stop])['S']

            # prepare S coordinate and append to each list per element
            for i in range(index.start,index.stop,index.step):
                # copy instead of modify existing
                elementlist = list(self.data[self.sequence[i]])
                if prepareNewS:
                    # maintain the original s from the original data
                    if start > stop:
                        elementlist[self.ColumnIndex('S')] = (
                            abs(sEnd - elementlist[self.ColumnIndex('S')])
                            + elementlist[self.ColumnIndex('L')])
                        elementlist[self.ColumnIndex('SMID')] = (
                            abs(sEnd - elementlist[self.ColumnIndex('SMID')])
                            + elementlist[self.ColumnIndex('L')])
                    else:
                        elementlist[self.ColumnIndex('S')] = (
                            abs(sStart - elementlist[self.ColumnIndex('S')]))
                        elementlist[self.ColumnIndex('SMID')] = (
                            abs(sStart - elementlist[self.ColumnIndex('SMID')]))

                a._AppendDataEntry(self.sequence[i], elementlist)

            a.smax = max(a.GetColumn('S'))
            a.smin = min(a.GetColumn('S'))
            return a

        try: # Try using the index as an integer
            return self.GetRowDict(self.sequence[index])
        except TypeError: # Try using the index as a name
            return self.GetRowDict(index)

    def _CheckName(self,name):
        if self.data.has_key(name):
            #name already exists - boo degenerate names!
            i = 1
            basename = name
            while self.data.has_key(name):
                name = basename+'_'+str(i)
                i = i + 1
            return name
        else:
            return name

    def _CopyMetaData(self,instance):
        params = ["header","columns","formats","filename"]
        for param in params:
            setattr(self,param,getattr(instance,param))
        #calculate the maximum s position - could be different based on the slice
        if 'S' in instance.columns:
            self.smax = instance[-1]['S']
        else:
            self.smax = 0

    def _DeepCopy(self,instance):
        #return type(self)(deepcopy(instance))
        self._CopyMetaData(instance)
        params = ["index","data","sequence","nitems","nsegments"]
        for param in params:
            setattr(self,param,_copy.deepcopy(getattr(instance,param)))

    def _AppendDataEntry(self,name,entry):
        if len(self.index) > 0:                   #check if there's any elements yet
            self.index.append(self.index[-1] + 1) #create an index
        else:
            self.index.append(0)
        self.sequence.append(name)  #append name to sequence
        self.nitems    += 1         #increment nitems
        self.data[name] = entry     #put the data in

    def __iadd__(self, other):
        self._CopyMetaData(other) #fill in any data from other instance
        for i in range(len(other)):
            key = other.sequence[i]
            self._AppendDataEntry(key,other.data[key])
        return self

    def NameFromIndex(self,index):
        """
        NameFromIndex(integerindex)

        return the name of the beamline element at index
        """
        return self.sequence[index]

    def NameFromNearestS(self,S):
        """
        NameFromNearestS(S)

        return the name of the beamline element clostest to S
        """
        i = self.IndexFromNearestS(S)
        return self.sequence[i]

    def IndexFromNearestS(self, S):
        """
        IndexFromNearestS(S)

        return the index of the beamline element which CONTAINS the
        position S.

        Note:  For small values beyond smax, the index returned will
        be -1 (i.e. the last element).

        """
        if S > self.smax and S < self.smax + 10:
            # allow some margin (+10) in case point is only just beyond the
            # beam line.  This is purely for clicking the plotted the machine
            # along the top of a figure.
            return -1
        elif S > self.smax + 10:
            raise ValueError("S is out of bounds.")
        elif S < self.smin:
            raise ValueError("S is out of bounds.")

        for i in range(1, self.nitems + 1):
            sLow = self[i - 1]['S']
            sHigh = self[i]['S']

            if (S >= sLow and S < sHigh):
                return i
        raise ValueError("S is out of bounds.")

    def _EnsureItsAnIndex(self, value):
        if type(value) == str:
            return self.IndexFromName(value)
        else:
            return value

    def IndexFromName(self,namestring):
        """
        Return the index of the element named namestring.  Raises
        ValueError if not found.

        """
        return self.sequence.index(namestring)

    def ColumnIndex(self,columnstring):
        """
        Return the index to the column matching the name

        REMEMBER: excludes the first column NAME
        0 counting

        """
        return self.columns.index(columnstring)

    def GetColumn(self,columnstring):
        """
        Return a numpy array of the values in columnstring in order
        as they appear in the beamline
        """
        i = self.ColumnIndex(columnstring)
        return _np.array([self.data[name][i] for name in self.sequence])

    def GetColumnDict(self,columnstring):
        """
        GetColumnDict(columnstring)
        return all data from one column in a dictionary

        note not in order
        """
        i = self.ColumnIndex(columnstring)
        d = dict((k,v[i]) for (k,v) in self.data.iteritems())
        #note we construct the dictionary comprehension in a weird way
        #here because SL6 uses python2.6 which doesn't have dict comprehension
        return d

    def GetRow(self,elementname):
        """
        Return all data from one row as a list
        """
        try:
            d = self[elementname]
        except KeyError:
            print 'No such item',elementname,' in this tfs file'
            return None
        return [d[key] for key in self.columns]

    def GetRowDict(self,elementname):
        """
        Return a dictionary of all parameters for a specifc element
        given by element name.

        note not in order
        """
        #no dictionary comprehension in python2.6 on SL6
        d = dict(zip(self.columns,self.data[elementname]))
        return d

    def GetSegment(self,segmentnumber):
        if type(segmentnumber) is str:
            segmentnumber = self.segments.index(segmentnumber)+1
        if segmentnumber not in range(1,len(self.segments)+1):
            raise ValueError("Invalid segment number "+str(segmentnumber))
        a = Tfs()
        a._CopyMetaData(self)
        segmentindex = self.columns.index('SEGMENT')
        hasname = 'NAME' in self.columns
        for key in self.sequence:
            if self.data[key][segmentindex] == segmentnumber:
                a._AppendDataEntry(key,self.data[key])
        return a

    def EditComponent(self, index, variable, value):
        """
        Edits variable of component at index and sets it to value.  Can
        only take indices as every single element in the sequence has
        a unique definition, and components which may appear
        degenerate/reused are in fact not in this data model.
        """
        variableIndex = self.columns.index(variable)
        componentName = self.sequence[index]
        self.data[componentName][variableIndex] = value

    def InterrogateItem(self,itemname):
        """
        InterrogateItem(itemname)

        Print out all the parameters and their names for a
        particlular element in the sequence identified by name.
        """
        for i,parameter in enumerate(self.columns):
            print parameter.ljust(10,'.'),self.data[itemname][i]

    def GetElementNamesOfType(self,typename):
        """
        GetElementNamesOfType(typename)

        Returns a list of the names of elements of a certain type. Typename can
        be a single string or a tuple or list of strings.

        Examples:

        >>> GetElementsOfType('SBEND')
        >>> GetElementsOfType(['SBEND','RBEND'])
        >>> GetElementsOfType(('SBEND','RBEND','QUADRUPOLE'))

        """
        if 'KEYWORD' in self.columns:
            i = self.ColumnIndex('KEYWORD')
        elif 'APERTYPE' in self.columns:
            i = self.ColumnIndex('APERTYPE')
        else:
            i = 0
        return [name for name in self.sequence if self.data[name][i] in typename]

    def GetElementsOfType(self,typename):
        """
        Returns a Tfs instance containing only the elements of a certain type.
        Typename can be a sintlge string or a tuple or list of strings.

        This returns a Tfs instance with all the same capabilities as this one.
        """
        names = self.GetElementNamesOfType(typename)
        a = Tfs()
        a._CopyMetaData(self)
        for key in names:
            a._AppendDataEntry(key,self.data[key])
        return a

    def GetCollimators(self):
        """
        Returns a Tfs instance containing any type of collimator (including
        COLLLIMATOR, RCOLLIMATOR and ECOLLIMATOR).
        """
        if 'KEYWORD' in self.columns:
            i = self.ColumnIndex('KEYWORD')
        else:
            i = 0

        names = [name for name in self.sequence if 'COLLIMATOR' in self.data[name][i]]
        a = Tfs()
        a._CopyMetaData(self)
        for key in names:
            a._AppendDataEntry(key,self.data[key])
        return a

    def GetElementsWithTextInName(self, text):
        """
        Returns a Tfs instance containing only the elements with the string in
        text in the their name.

        This returns a Tfs instance with all the same capabilities as this one.
        """
        a = Tfs()
        a._CopyMetaData(self)
        for item in self.sequence:
            if type(text) == str:
                if text in item:
                    a._AppendDataEntry(item, self.data[item])
            elif type(text) == list:
                for t in text:
                    if t in item:
                        a._AppendDataEntry(item, self.data[item])
            else:
                pass
        return a

    def ReportPopulations(self):
        """
        Print out all the population of each type of
        element in the beam line (sequence)
        """
        print 'Filename >',self.filename
        print 'Total number of items >',self.nitems
        if 'KEYWORD' in self.columns:
            i = self.ColumnIndex('KEYWORD')
        elif 'APERTYPE' in self.columns:
            i = self.ColumnIndex('APERTYPE')
        else:
            raise KeyError("No keyword or apertype columns in this Tfs file")

        keys = set([self.data[name][i] for name in self.sequence])
        populations = [(len(self.GetElementsOfType(key)),key) for key in keys]
        print 'Type'.ljust(15,'.'),'Population'
        for item in sorted(populations)[::-1]:
            print item[1].ljust(15,'.'),item[0]

    def Plot(self, title='', outputfilename=None, machine=True, dispersion=False, squareroot=True):
        """
        Plot the Beta amplitude functions from the file if they exist.

        squareroot -> whether to square root the beta functions or not (default = True)
        """
        import pymadx.Plot as _Plot
        if outputfilename is None:
            outputfilename = "{}_beta".format((self.filename.split("."))[0])
        _Plot.Beta(self, title, outputfilename, machine, dispersion, squareroot)

    def PlotCentroids(self, title='', outputfilename=None, machine=True):
        """
        Plot the centroid in the horizontal and vertical from the file if they exist.
        """
        import pymadx.Plot as _Plot
        if outputfilename is None:
            outputfilename = "{}_centroid".format((self.filename.split("."))[0])
        _Plot.Centroids(self,title,outputfilename,machine)

    def PlotSigma(self, title='', outputfilename=None, machine=True, dispersion=False):
        """
        Plot the beam size.
        """
        import pymadx.Plot as _Plot
        if outputfilename is None:
            outputfilename = "{}_sigma".format((self.filename.split("."))[0])
        _Plot.Sigma(self, title, outputfilename, machine, dispersion)

    def IndexFromGmadName(self, gmadname, verbose=False):
        """
        Returns the indices of elements which match the supplied gmad name.
        Useful because tfs2gmad strips punctuation from the component names, 
        and irritating otherwise to work back. When multiple elements of the 
        name match, returns the indices of all the components in a list.
        Arguments:
        gmadname     :    The gmad name of a component to search for.
        verbose      :    prints out matching name indices and S locations.  Useful for discriminating between identical names.
        """
        indices = []
        #Because underscores are allowed in gmad names:
        punctuation = _string.punctuation.replace('_', '')
        for index, element in enumerate(self):
            #translate nothing to nothing and delete all forbidden chars from name.
            name = element['NAME']
            strippedName = name.translate(_string.maketrans("",""), punctuation)
            if _re.match(gmadname + "_?[0-9]*", strippedName):
                indices.append(index)
        if verbose:
            for index in indices:
                sPos = self.data[self.NameFromIndex(index)][self.ColumnIndex('S')]
                print " matches at S =", sPos, "@index", index
        if len(indices) == 1:
            return indices[0]
        elif len(indices) > 1:
            return indices
        else:
            raise ValueError(gmadname + ' not found in list')

    def ComponentPerturbs(self, indexInSequence):
        """
        Returns names of variables which would perturb a particle.
        Some components written out in TFS are redundant,
        so it's useful to know which components perturb a particle's motion.
        This is likely not an exhaustive check so refer to source if unsure.

        Checks integrated stengths (but not if L=0), HKICK and VKICK

        indexInSequence - index of component to be checked.
        terse           - print out the parameters which perturb if False
        """

        return self.ElementPerturbs(self[indexInSequence])

    def ElementPerturbs(self, component):
        """
        Search an invidivual dictionary representing a row in the TFS file
        for as to whether it perturbs.
        """

        perturbingParameters = []  # list of perturbing params which are abs>0

        # these checks may be incomplete..  just the ones i know of.

        # check the kls..  if length is zero then kls don't matter.
        if component['L'] > 0:
           for variable in component.keys():
               kls = _re.compile(r'K[0-9]*S?L') # matches all integrated strengths.
               if (_re.match(kls, variable) and
                   abs(component[variable]) > 0):
                   perturbingParameters.append(variable)

        #check the kick angles.
        if abs(component['VKICK']) > 0:
            perturbingParameters.append('VKICK')
        if abs(component['HKICK']) > 0:
            perturbingParameters.append('HKICK')

        if (not perturbingParameters):
            return False
        else:
            return perturbingParameters

    def RenameElement(self, index, new):
        """
        Rename indexed element.
        """
        # I don't fully understand how defensive this method needs to
        # be, so I err on the side of caution and prevent any name
        # which already exists in either self.sequence or self.data
        # from being used as a new name.
        old = self.sequence[index]
        if (new in self.sequence
            or new in self.data
            or new in self.GetColumn("NAME")
            or new in self.GetColumn("UNIQUENAME")):
            raise ValueError("New name already present: {}".format(new))
        self.sequence[index] = new
        self.data[old][self.ColumnIndex("NAME")] = new
        self.data[old][self.ColumnIndex("UNIQUENAME")] = new
        self.data[new] = self.data.pop(old)

    def SplitElement(self, SSplit):
        """
        Splits the element found at SSplit given, performs the necessary
        operations on the lattice to leave the model functionally
        identical and returns the indices of the first and second
        component.  Element new name will be the same as the original
        except appended with a number corresponding to its location in
        the list of previously identically defined components used in
        the sequence and either "split_1" or "split_2" depending on
        which side of the split it is located.  It is necessary to
        append both of these numbers to ensure robust name mangling.

        WARNING: DO NOT SPLIT THE ELEMENT WHICH MARKS THE BEGINNING OF
        YOUR LATTICE.  YOUR OPTICS WILL BE WRONG!

        """

        # the element to be split:
        originalIndex = self.IndexFromNearestS(SSplit)
        originalName = self.sequence[originalIndex]
        originalLength = self[originalName]['L']
        originalS = self[originalName]['S']
        originalHKick = self[originalName]['HKICK']
        originalVKick = self[originalName]['VKICK']
        originalAngle = self[originalName]['ANGLE']
        originalKLs = {"K{}L".format(i): self[originalName]['K{}L'.format(i)]
                       for i in range(1, 7)}
        originalKSLs = {"K{}SL".format(i): self[originalName]['K{}SL'.format(i)]
                       for i in range(1, 7)}
        elementType = self[originalName]['KEYWORD']

        # First of the two elements that the original is split into.
        # Remembering that in MADX S is at the end of the component.
        firstS = SSplit
        firstLength = originalLength - (originalS - SSplit)
        firstName = originalName + str("_split_1")
        firstUniqueName = firstName
        firstIndex = originalIndex

        # second of two elements that original is split into:
        secondS = originalS
        secondLength = originalS - SSplit
        secondName = originalName + str("_split_2")
        secondUniqueName = secondName
        secondIndex = originalIndex + 1

        # update the sequence
        self.sequence[firstIndex] = firstName
        self.sequence.insert(secondIndex, secondName)

        # Making data entries for new components
        self.data[firstName] = _copy.deepcopy(self.data[originalName])
        self.data[secondName] = _copy.deepcopy(self.data[originalName])
        del self.data[originalName]

        # Apply the relevant edits to the newly split component.
        self.EditComponent(firstIndex, 'L', firstLength)
        self.EditComponent(firstIndex, 'S', firstS)
        self.EditComponent(firstIndex, 'SMID', firstS - firstLength/2.0)
        self.EditComponent(firstIndex, 'SORIGINAL', originalS)
        self.EditComponent(firstIndex, 'NAME', firstName)
        self.EditComponent(firstIndex, 'UNIQUENAME', firstUniqueName)

        self.EditComponent(secondIndex, 'L', secondLength)
        self.EditComponent(secondIndex, 'S', secondS)
        self.EditComponent(secondIndex, 'SMID', secondS - secondLength/2.0)
        self.EditComponent(secondIndex, 'SORIGINAL', originalS)
        self.EditComponent(secondIndex, 'NAME', secondName)
        self.EditComponent(secondIndex, 'UNIQUENAME', secondUniqueName)

        # Assign the appropriate amount of kick to each of the two components
        firstRatio = firstLength/originalLength
        secondRatio = 1 - firstRatio
        self.EditComponent(firstIndex, 'HKICK', firstRatio * originalHKick)
        self.EditComponent(firstIndex, 'VKICK', firstRatio * originalVKick)
        self.EditComponent(firstIndex, 'ANGLE', firstRatio * originalAngle)
        self.EditComponent(firstIndex, 'E2', 0.5 * firstRatio * originalAngle)
        self.EditComponent(firstIndex, 'FINTX', 0.0)

        self.EditComponent(secondIndex, 'HKICK', secondRatio * originalHKick)
        self.EditComponent(secondIndex, 'VKICK', secondRatio * originalVKick)
        self.EditComponent(secondIndex, 'ANGLE', secondRatio * originalAngle)
        self.EditComponent(secondIndex, 'E1', 0.5 * secondRatio * originalAngle)
        self.EditComponent(secondIndex, 'FINT', 0.0)

        for name, value in originalKLs.iteritems():
            self.EditComponent(firstIndex, name, firstRatio * value)
            self.EditComponent(secondIndex, name, secondRatio * value)
        for name, value in originalKSLs.iteritems():
            self.EditComponent(firstIndex, name, firstRatio * value)
            self.EditComponent(secondIndex, name, secondRatio * value)

        assert self[secondName]["S"] == originalS
        assert self[firstName]["L"] + self[secondName]["L"] == originalLength
        assert (self[firstName]["HKICK"]
                + self[secondName]["HKICK"]) == originalHKick
        assert (self[firstName]["VKICK"]
                + self[secondName]["VKICK"]) == originalVKick
        return firstIndex, secondIndex

    def ConcatenateMachine(self, *args):
        """
        This is used to concatenate machines.
        """
        # Get final position of the machine
        lastSpos = self.GetColumn('S')[-1]

        for machineIndex,machine in enumerate(args):
            if isinstance(machine, _np.str):
                machine = CheckItsTfs(machine)

            # copy the machine. concatenating self to self doesn't update s positions correctly
            machine = _copy.deepcopy(machine)

            # check names sets are equal
            if len(set(self.names).difference(set(machine.names))) != 0:
                raise AttributeError("Cannot concatenate machine, variable names do not match")

            sind = self.names.index('S')
            sindOrig = self.names.index('SORIGINAL')
            sindMid = self.names.index('SMID')

            for elementindex in range(machine.nitems):
                element = machine[elementindex]
                uniqueName = element['UNIQUENAME']

                # check if the element name is already in the sequence
                if element['UNIQUENAME'] in self.data.keys():
                    uniqueName += "_" + _np.str(machineIndex+1)

                self.data[uniqueName] = machine.data[element['UNIQUENAME']]

                # update elements s positions with last s position of previous machine
                self.data[uniqueName][sind] += lastSpos
                self.data[uniqueName][sindOrig] += lastSpos
                self.data[uniqueName][sindMid] += lastSpos

                self.sequence.append(uniqueName)
                self.nitems += 1

            # update last s position from this machine
            lastSpos += self.GetColumn('S')[-1]
        self.smax = self.GetColumn('S')[-1]
        self.header['LENGTH'] = self.GetColumn('S')[-1]

def CheckItsTfs(tfsfile):
    """
    Ensure the provided file is a Tfs instance.  If it's a string, ie path to
    a tfs file, open it and return the Tfs instance.

    tfsfile can be either a tfs instance or a string.
    """
    if type(tfsfile) == str:
        madx = Tfs(tfsfile)
    elif type(tfsfile) == Tfs:
        madx = tfsfile
    else:
        raise IOError("Not pymadx.Data.Tfs file type: "+str(tfsfile))
    return madx

_madxAperTypes = { 'CIRCLE',
                   'RECTANGLE',
                   'ELLIPSE',
                   'RECTCIRCLE',
                   'LHCSCREEN',
                   'MARGUERITE',
                   'RECTELLIPSE',
                   'RACETRACK',
                   'OCTAGON'}

class Aperture(Tfs):
    """
    A class based on (ie inherits) the Tfs class for reading aperture information.
    This allows madx aperture information in Tfs format to be loaded, filtered and
    queried. This also provides the ability to suggest whether an element should be
    split and therefore what the aperture should be.

    This class maintains a cache of aperture information as a function of S position.

    'quiet' being defined in kwargs will silence a warning about unknown aperture types.

    """
    def __init__(self, *args, **kwargs):
        # set so TFS class doesn't calculate sigma as optics shouldn't exist in aperture tfs file
        kwargs.update({'calculatesigma':False})
        Tfs.__init__(self, *args, **kwargs)
        self.debug = False
        if 'debug' in kwargs:
            self.debug = kwargs['debug']

        # the tolerance below which, the aperture is considered 0
        self._tolerance = 1e-6
        self._UpdateCache()
        if 'quiet' not in kwargs:
            self.CheckKnownApertureTypes()

    def _UpdateCache(self):
        # create a cache of which aperture is at which s position
        # do this by creatig a map of the s position of each entry
        # with the associated
        self.cache = {}
        for item in self:
            s = item['S']
            if s in self.cache.keys():
                #if existing one is zero and other isn't replace it
                if ZeroAperture(self.cache[s]) and NonZeroAperture(item):
                    self.cache[s] = item
            else:
                self.cache[s] = item

        # dictionary is not ordered to keep list of ordered s positions
        self._ssorted = self.cache.keys()
        self._ssorted.sort()

        # pull out some aperture values for conevience
        # try this as class may be constructed with no data
        try:
            for key in ['APER_1', 'APER_2', 'APER_3', 'APER_4']:
                setattr(self, '_'+str.lower(key), self.GetColumn(key))
        except ValueError:
            pass

    def Plot(self, machine=None, outputfilename=None, plot="xy", plotapertype=True):
        """
        This plots the aperture extent in x and y.

        This replaces the base class Tfs Plot method.

        Inputs:
          title (str) - The title of the resultant plot (default: None)
          outputfilename (str) - Name without extension of the output file if desired (default: None)
          machine (str or pymadx.Data.Tfs) - TFS file or TFS istance to plot a machine lattice from (default: None)
          plot (str) - Indicates whcih aperture to plot - 'x' for X, 'y' for Y and 'xy' for both (default: 'xy')
          plotapertype (bool) - If enabled plots the aperture type at every definted aperture point as a color-coded dot (default: False)

        """
        import pymadx.Plot as _Plot
        _Plot.Aperture(self, machine, outputfilename, plot=plot, plotapertype=plotapertype)

    def PlotN1(self, machine=None, outputfilename=None):
        """
        Plot the N1 aperture value from MADX. 
        
        Requires N1 and S column.
        
        Optional "machine" argument is string to or pymadx.Data.Tfs instance
        for twiss description to provide a machine diagram on top.
        """
        import pymadx.Plot as _Plot
        _Plot.ApertureN1(self, machine, outputfilename)

    def CheckKnownApertureTypes(self):
        failed = False
        ts = set(self.GetColumn('APERTYPE'))
        for t in ts:
            if t not in _madxAperTypes:
                if t.isspace() or not t:
                    pass #quiet for empty strings or strings with only whitespace (can be default)
                else:
                    failed = True
                    print 'Warning: Aperture type \"',t,'\" is not a valid MADX aperture type.'

        if failed:
            PrintMADXApertureTypes()

    def SetZeroTolerance(self, tolerance):
        """
        Set the value below which aperture values are considered 0.
        """
        self._tolerance = tolerance

    def GetNonZeroItems(self):
        """
        Return a copy of this class with all non-zero items removed.

        """
        return self.RemoveBelowValue(self._tolerance)

    def GetEntriesBelow(self, value=8, keys='all'):
        return self.RemoveAboveValue(value,keys)

    def RemoveNoApertureTypeEntries(self):
        """
        Return a copy of this instance with any null aperture types removed.

        Aperture type of "" will be removed.
        """
        atKey = 'APERTYPE'
        if atKey not in self.columns:
            print('No APERTYPE column')
            return self

        a = Aperture(debug=self.debug, quiet=True)
        a._CopyMetaData(self)
        for item in self:
            if item[atKey] == "":
                pass #don't copy
            else:
                #copy over as normal
                key = self.sequence[self._iterindex]
                a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def RemoveBelowValue(self, limits, keys='all'):
        """
        Return a copy of the aperture instance with all entries where
        any of the aperture values are below value. The default is
        the tolerance as defined by SetZeroTolerance().
        """
        print 'Aperture> removing any aperture entries below',limits
        if keys == 'all':
            aperkeystocheck = ['APER_%s' %n for n in range(1,5)] #prepare #APER_1, APER_2 etc
        elif type(keys) in (float, int, str):
            aperkeystocheck = [keys]
        elif type(keys) in (list, tuple):
            aperkeystocheck = list(keys)

        limitvals = _np.array(limits) # works for single value, list or tuple in comparison

        # check validity of the supplied keys
        aperkeys = []
        for key in aperkeystocheck:
            if key in self.columns:
                aperkeys.append(key)
            else:
                print key,' will be ignored as not in this aperture Tfs file'

        # 'quiet' stops it complaining about not finding metadata
        a = Aperture(debug=self.debug, quiet=True)
        a._CopyMetaData(self)
        for item in self:
            apervals = _np.array([item[key] for key in aperkeys])
            abovelimit = apervals < limitvals
            abovelimittotal = abovelimit.any() # if any are true
            if not abovelimittotal:
                key = self.sequence[self._iterindex]
                a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def RemoveAboveValue(self, limits=8, keys='all'):
        print 'Aperture> removing any aperture entries above',limits
        if keys == 'all':
            aperkeystocheck = ['APER_%s' %n for n in [1,2,3,4]]
        elif type(keys) in (float, int, str):
            aperkeystocheck = [keys]
        elif type(keys) in (list, tuple):
            aperkeystocheck = list(keys)
        else:            raise ValueError("Invalid key")

        limitvals = _np.array(limits) # works for single value, list or tuple in comparison

        # check validity of the supplied keys
        aperkeys = []
        for key in aperkeystocheck:
            if key in self.columns:
                aperkeys.append(key)
            else:
                print key,' will be ignored as not in this aperture Tfs file'

        if len(aperkeys) == 0:
            print('No aperture values to check')
            return self

        # 'quiet' stops it complaining about not finding metadata
        a = Aperture(debug=self.debug, quiet=True)
        a._CopyMetaData(self)
        for item in self:
            apervals = _np.array([item[key] for key in aperkeys])
            abovelimit = apervals > limitvals
            abovelimittotal = abovelimit.any() # if any are true
            if not abovelimittotal:
                key = self.sequence[self._iterindex]
                a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def GetUniqueSPositions(self):
        return self.RemoveDuplicateSPositions()

    def RemoveDuplicateSPositions(self):
        """
        Takes the first aperture value for entries with degenerate S positions and
        removes the others.
        """
        print 'Aperture> removing entries with duplicate S positions'
        # check if required at all
        if len(self) == len(self._ssorted):
            # no duplicates!
            return self

        a = Aperture(debug=self.debug, quiet=True)
        a._CopyMetaData(self)
        u,indices = _np.unique(self.GetColumn('S'), return_index=True)
        for ind in indices:
            key = self.sequence[ind]
            a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def _GetIndexInCacheOfS(self, sposition):
        index = _bisect.bisect_right(self._ssorted, sposition)

        if index > 0:
            return index - 1
        else:
            return index

    def GetApertureAtS(self, sposition):
        """
        Return a dictionary of the aperture information specified at the closest
        S position to that requested - may be before or after that point.
        """

        a = Aperture(debug=self.debug, quiet=True)
        a._CopyMetaData(self)
        rowdict = self.cache[self._ssorted[self._GetIndexInCacheOfS(sposition)]]
        #key = self.sequence[self._GetIndexInCacheOfS(sposition)]
        #a._AppendDataEntry(key, self.data[key])
        #a._UpdateCache()

        #.cache.values()[0]
        #return self[self._GetIndexInCacheOfS(sposition)]
        return rowdict

    def GetExtentAtS(self, sposition):
        """
        Get the x and y maximum +ve extent (assumed symmetric) for a given
        s position.  Calls GetApertureAtS and then GetApertureExtent.
        """
        rd = self.GetApertureAtS(sposition)
        aper1 = rd('APER_1')
        aper2 = rd('APER_2')
        aper3 = rd('APER_3')
        aper4 = rd('APER_4')
        apertureType = rd('APERTYPE')

        x,y     = GetApertureExtent(apertureType, aper1, aper2, aper3, aper4)
        return x,y

    def GetApertureForElementNamed(self, name):
        """
        Return a dictionary of the aperture information by the name of the element.
        """
        return self.GetRow(name)

    def GetExtent(self, name):
        """
        Get the x and y maximum +ve extent (assumed symmetric) for a given
        entry by name.  Calls GetApertureForElementNamed and then GetApertureExtent.
        """
        element = self.GetApertureForElementNamed(name)
        x,y     = GetApertureExtent(element)
        return x,y

    def GetExtentAll(self):
        """
        Get the x and y maximum +ve extent (assumed symmetric) for the full
        aperture instance.

        returns x,y where x and y are 1D numpy arrays
        """
        x,y = GetApertureExtents(self)

        return x,y

    def ReplaceType(self, existingType, replacementType):
        print 'Aperture> replacing',existingType,'with',replacementType
        et = existingType    #shortcut
        rt = replacementType #shortcut
        try:
            index = self.columns.index('APERTYPE')
        except ValueError:
            print 'No apertype column, therefore no type to replace'
            return
        for item in self:
            try:
                if item['APERTYPE'] == et:
                    self.data[item['NAME']][index] = rt
            except KeyError:
                return

    def ShouldSplit(self, rowDictionary):
        """
        Suggest whether a given element should be split as the aperture information
        in this class suggests multiple aperture changes within the element.

        Returns bool, [], []

        which are in order:

        bool - whether to split or not
        []   - list of lengths of each suggested split
        []   - list of the aperture dictionaries for each one

        """
        l      = rowDictionary['L']
        sEnd   = rowDictionary['S']
        sStart = sEnd -l

        indexStart = self._GetIndexInCacheOfS(sStart)
        indexEnd   = self._GetIndexInCacheOfS(sEnd)
        # get the s positions of any defined aperture points within
        # the length of the element
        apertureSValuesInRange = self._ssorted[indexStart:indexEnd]

        # calculate differentials of aperture values in range of the element
        # test if any are non-zero
        bdA1 = _np.diff(self._aper_1[indexStart:indexEnd]) != 0
        bdA2 = _np.diff(self._aper_2[indexStart:indexEnd]) != 0
        bdA3 = _np.diff(self._aper_3[indexStart:indexEnd]) != 0
        bdA4 = _np.diff(self._aper_4[indexStart:indexEnd]) != 0

        # find if there are any changes in aperture for any parameter
        shouldSplit = _np.array([bdA1, bdA2, bdA3, bdA4]).any()

        if self.debug:
            print 'length: ',l,', S (start): ',sStart,', S (end): ',sEnd
            print 'Index (start): ',indexStart,', Index(end): ',indexEnd
            print 'Any difference in aper1: ',bdA1
            print 'Any difference in aper2: ',bdA2
            print 'Any difference in aper3: ',bdA3
            print 'Any difference in aper4: ',bdA4

        if not shouldSplit:
            # return false and the aperture model to be use for the whole item
            sMid = (sEnd - sStart) / 2
            return False, [l], [self.GetApertureAtS(sMid)]
        else:
            if self.debug:
                print 'Recommend splitting element'
            # should split!
            # work out s locations at split points

            # put all selection boolean arrays into one large 2D array
            # of nonzero differential vs aperture parameter
            bdA = _np.array([bdA1, bdA2, bdA3, bdA4])
            # get the a unique set of the indices where any aperture changes
            # nonzero->bool array, take only which items (rows) have nonzero diffs, take set of to remove duplication
            indices = _np.array(list(set(bdA.nonzero()[1])))
            indices += indexStart # add on offset to get index for whole data
            if self.debug:
                print indices
            sSplits = _np.array([self._ssorted[x] for x in indices]) # s positions of aperture changes
            if len(sSplits) > 1:
                while sSplits[0] < sStart:
                    sSplits = sSplits[1:] # remove any elements before the start position of this element
            sSplitStart = _np.array(sSplits) #copy the starts
            sSplitStart = _np.insert(sSplitStart, 0, sStart) # prepnd s of first element
            # work out the length of each section
            lSplits = sSplits - sStart

            # replace any <0 lengths ie nearest aperture definition behind start of this object
            # ignore these and only take aperture definitions in front of the element
            lSplits     = lSplits[lSplits > 0]

            if self.debug:
                print 'Aperture> length of splits: ',lSplits

            # lSplits is just the length of the proposed split points from the start
            # make them a local S within the element by prepending 0 and appending L(ength)
            lSplits = _np.insert(lSplits, 0, 0)
            lSplits = _np.append(lSplits, l) # make length last one

            lSplits = _np.diff(lSplits)

            if self.debug:
                print 'Aperture> length of splits after checks: ',lSplits

            # paranoid checks - trim / adjust last element to conserve length accurately
            if lSplits.sum() != l:
                lSplits[-1] = lSplits[-1] + (l - lSplits.sum())

            # get the mid point of each split segment for asking what the aperture should be
            sSplitMid = sStart + lSplits*0.5
            apertures = [self.GetApertureAtS(s) for s in sSplitMid]

            # check result of attempted splitting
            result = True if len(sSplits)>1 else False
            if len(apertures) > len(sSplits):
                apertures = apertures[:len(sSplits)] #should index 1 ahead - counteracts 0 counting

            return result, lSplits, apertures

def CheckItsTfsAperture(tfsfile):
    """
    Ensure the provided file is an Aperture instance.  If it's a string, ie path to
    a tfs file, open it and return the Tfs instance.

    tfsfile can be either a tfs instance or a string.
    """
    if type(tfsfile) == str:
        aper = Aperture(tfsfile)
    elif type(tfsfile) == Aperture:
        aper = tfsfile
    else:
        raise IOError("Not pymadx.Aperture.Aperture file type: "+str(tfsfile))
    return aper

def PrintMADXApertureTypes():
    print 'Valid MADX aperture types are:'
    for t in _madxAperTypes:
        print t

def GetApertureExtents(aperture):
    """
    Loop over a pymadx.Aperture.Aperture instance and calculate the maximum
    +ve extent (assumed symmetric) in x and y.

    returns x,y where x and y and 1D numpy arrays
    """
    aper1 = aperture.GetColumn('APER_1')
    aper2 = aperture.GetColumn('APER_2')
    aper3 = aperture.GetColumn('APER_3')
    aper4 = aperture.GetColumn('APER_4')
    apertureType = aperture.GetColumn('APERTYPE')

    x = []
    y = []
    for i in range(len(aperture)):
        xt,yt = GetApertureExtent(aper1[i], aper2[i], aper3[i], aper4[i], apertureType[i])
        x.append(xt)
        y.append(yt)

    x = _np.array(x)
    y = _np.array(y)
    return x,y

def GetApertureExtent(aper1, aper2, aper3, aper4, aper_type):
    """
    Get the maximum +ve half extent in x and y for a given aperture model and (up to)
    four aperture parameters.

    returns x,y
    """
    # protect against empty aperture type
    if aper_type == "":
        return 0,0

    if aper_type not in _madxAperTypes:
        raise ValueError('Unknown aperture type: ' + aper_type)

    x = aper1
    y = aper2

    if aper_type == 'CIRCLE':
        x = aper1
        y = aper1
    if aper_type in ['RECTANGLE', 'ELLIPSE', 'OCTAGON']:
        x = aper1
        y = aper2
    elif aper_type in ['LHCSCREEN', 'RECTCIRCLE', 'MARGUERITE']:
        x = min(aper1, aper3)
        y = min(aper2, aper3)
    if aper_type == 'RECTELLIPSE':
        x = min(aper1, aper3)
        y = min(aper2, aper4)
    elif aper_type == 'RACETRACK':
        x = aper3 + aper1
        y = aper2 + aper3

    return x,y


def NonZeroAperture(item):
    tolerance = 1e-9
    test1 = item['APER_1'] > tolerance
    test2 = item['APER_2'] > tolerance
    test3 = item['APER_3'] > tolerance
    test4 = item['APER_4'] > tolerance

    return test1 or test2 or test3 or test4

def ZeroAperture(item):
    tolerance = 1e-9
    test1 = item['APER_1'] < tolerance
    test2 = item['APER_2'] < tolerance
    test3 = item['APER_3'] < tolerance
    test4 = item['APER_4'] < tolerance

    return test1 and test2 and test3 and test4
