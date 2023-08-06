Beginners Guide / Help
======================

.. autosummary::
    jscatter.showDoc


Reading ASCII files
-------------------
- dataArray (js.dA) reads **one** dataset from a file (you can choose which one).

- dataList  (js.dL) reads **all** datasets from one or multiple files (even if different in shape).

****

A common problem is how to read ASCII files with data as the format is often not
very intuitive designed. Often there is additional metadata before or after a matrix like block.

Jscatter uses a simple concept to classify lines :
 * 2 numbers at the beginning of a line are data (matrix like data block).
 * a name followed by a number (and more) is an attribute with name and content.
 * everything else is comment (but can later be converted to an attribute).

Often it is just necessary to replace some characters to fit into this idea.
This can be done during reading using some simple options in dataArray/dataList creation:
 * replace={‘old’:’new’,’,’:’.’}     ==>  replace char and strings
 * skiplines=lambda words: any(w in words for w in [‘’,’ ‘,’NAN’,’‘*])  ==> skip complete bad lines
 * takeline='ATOM'   ==> select specific lines
 * ignore ='#'       ==> skip lines starting with this character
 * usecols =[1,2,5]  ==> select specific columns
 * lines2parameter=[2,3,4]  ==> use these data lines as comment

See :py:func:`jscatter.dataarray.dataArray` for all options and how to use them.

If there is more information in comments or filename this can be extracted by using the comment lines.
 * data.getfromcomment('nameatfirstcolumn') ==> extract a list of words in this line
 * data.name  ==> filename, see below examples.


**Some examples and how to read them**

filename: data1_273K_10mM.dat (e.g. Instrument JNSE@MLZ, Garching) ::

 this is just a comment or description of the data
 temp     293
 pressure 1013 14
 detectorsetting up
 name     temp1bsa
 0.854979E-01  0.178301E+03  0.383044E+02
 0.882382E-01  0.156139E+03  0.135279E+02
 0.909785E-01  0.150313E+03  0.110681E+02
 0.937188E-01  0.147430E+03  0.954762E+01
 0.964591E-01  0.141615E+03  0.846613E+01
 0.991995E-01  0.141024E+03  0.750891E+01
 0.101940E+00  0.135792E+03  0.685011E+01
 0.104680E+00  0.140996E+03  0.607993E+01

Read by ::

 data=js.dA('data1_273K_10mM.dat')
 data.getfromComment('detectorsetting')           # creates attribute detectorsetting with string value 'up' found in comments
 data.Temp=float(data.name.split('_')[1][:-1])    # extracts the temperature from filename
 data.conc=float(data.name.split('_')[2][:-2])    # same for concentration
 data.pressure[0]                                 # use pressure value 1013 # this was created automatically
 data.Temp                                        # use temperature value   # this was created explicit

aspirin.pdb: Atomic coordinates for aspirin (`AIN <http://ligand-expo.rcsb.org/reports/A/AIN/AIN_ideal.pdb>`_ from `Protein Data Bank, PDB <http://www.rcsb.org/ligand/AIN>`_ )::

 Header
 Remarks blabla
 Remarks in pdb files are sometimes more than 100 lines
 ATOM      1  O1  AIN A   1       1.731   0.062  -2.912  1.00 10.00           O
 ATOM      2  C7  AIN A   1       1.411   0.021  -1.604  1.00 10.00           C
 ATOM      3  O2  AIN A   1       2.289   0.006  -0.764  1.00 10.00           O
 ATOM      4  C3  AIN A   1      -0.003  -0.006  -1.191  1.00 10.00           C
 ATOM      5  C4  AIN A   1      -1.016   0.010  -2.153  1.00 10.00           C
 ATOM      6  C5  AIN A   1      -2.337  -0.015  -1.761  1.00 10.00           C
 ATOM      7  C6  AIN A   1      -2.666  -0.063  -0.416  1.00 10.00           C
 ATOM      8  C1  AIN A   1      -1.675  -0.085   0.544  1.00 10.00           C
 ATOM      9  C2  AIN A   1      -0.340  -0.060   0.168  1.00 10.00           C
 ATOM     10  O3  AIN A   1       0.634  -0.083   1.111  1.00 10.00           O
 ATOM     11  C8  AIN A   1       0.314   0.035   2.410  1.00 10.00           C
 ATOM     12  O4  AIN A   1      -0.824   0.277   2.732  1.00 10.00           O
 ATOM     13  C9  AIN A   1       1.376  -0.134   3.466  1.00 10.00           C
 ATOM     14  HO1 AIN A   1       2.659   0.080  -3.183  1.00 10.00           H
 ATOM     15  H4  AIN A   1      -0.765   0.047  -3.203  1.00 10.00           H
 ATOM     16  H5  AIN A   1      -3.119   0.001  -2.505  1.00 10.00           H
 ATOM     17  H6  AIN A   1      -3.704  -0.082  -0.117  1.00 10.00           H
 ATOM     18  H1  AIN A   1      -1.939  -0.123   1.591  1.00 10.00           H
 ATOM     19  H91 AIN A   1       0.931  -0.004   4.453  1.00 10.00           H
 ATOM     20  H92 AIN A   1       1.807  -1.133   3.391  1.00 10.00           H
 ATOM     21  H93 AIN A   1       2.158   0.610   3.318  1.00 10.00           H
 CONECT    1    2   14 may apear at the end
 HETATOM lines may apear at the end
 END

Read by ::

 # 1.
 # take 'ATOM' lines, but only column 6-8 as x,y,z coordinates.
 js.dA('AIN_ideal.pdb',takeline='ATOM',usecols=[6,7,8])
 # 2.
 # replace 'ATOM' string by number and set XYZ for convenience
 js.dA('AIN_ideal.pdb',replace={'ATOM':'0'},usecols=[6,7,8],XYeYeX=[0,1,None,None,2])
 # 3.
 # using regular expressions we can decode the atom specifier into a scattering length
 import re
 rHO=re.compile('HO\d') # 14 is HO1
 rH=re.compile('H\d+')  # represents somthing like 'H11' or 'H1' see regular expressions
 rC=re.compile('C\d+')
 rO=re.compile('O\d+')
 # replace atom specifier by number and use it as last column
 ain=js.dA('AIN_ideal.pdb',replace={'ATOM':'0',rC:1,rH:5,rO:2,rHO:5},usecols=[6,7,8,2],XYeYeX=[0,1,None,None,2])
 # 4.
 # read only atoms and use it to retrieve atom data from js.formel.ELements
 atoms=js.dA('AIN_ideal.pdb',replace={'ATOM':'0'},usecols=[2],XYeYeX=[0,1,None,None,2])[0].array
 al=[js.formel.Elements[a[0].lower()] for a in atoms]

data2.txt::

 # this is just a comment or description of the data
 # temp     ;    293
 # pressure ; 1013 14  bar
 # name     ; temp1bsa
 &doit
 0,854979E-01  0,178301E+03  0,383044E+02
 0,882382E-01  0,156139E+03  0,135279E+02
 0,909785E-01  *             0,110681E+02
 0,937188E-01  0,147430E+03  0,954762E+01
 0,964591E-01  0,141615E+03  0,846613E+01
 nan           nan           0

Read by ::

 # ignore is by default '#', so switch it of
 # skip lines with non numbers in data
 # replace some char by others or remove by replacing with empty string ''.
 js.dA('data2.txt',replace={'#':'',';':'',',':'.'},skiplines=[‘*’,'nan'],ignore='' )


pdh format used in some SAXS instruments (first real data point is line 4)::

 SAXS BOX
       2057         0         0         0         0         0         0         0
   0.000000E+00   3.053389E+02   0.000000E+00   1.000000E+00   1.541800E-01
   0.000000E+00   1.332462E+00   0.000000E+00   0.000000E+00   0.000000E+00
 -1.069281E-01   2.277691E+03   1.168599E+00
 -1.037351E-01   2.239132E+03   1.275602E+00
 -1.005422E-01   2.239534E+03   1.068182E+00
 -9.734922E-02   2.219594E+03   1.102175E+00
 ......

Read by::

 # this saves the prepended lines in attribute line_2,...
 empty=js.dA('exampleData/buffer_averaged_corrected_despiked.pdh',usecols=[0,1],lines2parameter=[2,3,4])
 # next just ignores the first lines (and last 50) and uses every second line,
 empty=js.dA('exampleData/buffer_averaged_corrected_despiked.pdh',usecols=[0,1],block=[5,-50,2])

Read csv data by (comma separated list) ::

 js.dA('data2.txt',replace={',':' '})
 # If tabs separate the columns
 js.dA('data2.txt',replace={',':' ','\t':' '})

Creating from numpy arrays
--------------------------
This demonstrates how to create dataArrays form calculated data::

 #
 x=np.r_[0:10:0.5]                 # a list of values
 D,A,q=0.45,0.99,1.2               # parameters
 data=js.dA(np.vstack([x,np.exp(-q**2*D*x)+np.random.rand(len(x))*0.05,x*0+0.05]))
 data.diffusiocoefficient=D
 data.amplitude=A
 data.wavevector=q

 # alternative (diffusion with noise and error )
 data=js.dA(np.c_[x,np.exp(-q**2*D*x)*0.05,x*0+0.05].T)
 f=lambda xx,DD,qq,e:np.exp(-qq**2*DD*xx)+np.random.rand(len(x))*e
 data=js.dA(np.c_[x,f(x,D,q,0.05),np.zeros_like(x)+0.05].T)

Manipulating dataArray/dataList
-------------------------------
Changing values uses the same syntax as in numpy arrays with all availible methods and additional .X,.Y ....
dataList elements should be changed individually as dataArray which can be done in loops ::

 i7=js.dL(js.examples.datapath+'/polymer.dat')
 for ii in i7:
    ii.X/=10          # change scale
    ii.Y/=ii.conc     # normalising by concentration
    ii.Y=-np.log(ii.Y)*2
 i1=js.dA(js.examples.datapath+'/a0_336.dat')
 # all the same to multiply .X by 2
 i1.X*=2
 i1[0]*=2
 i1[0]=i1[0]*2        # most clear writing
 # multiply each second Y value by 2 (not really usefull, but to show it)
 i1[1,::2]=i1[1,::2]*2
 # making a Kratky plot
 p=js.grace()
 i1k=i1.copy()
 i1k.Y=i1.Y*i1k.X**2     # no problem if i1 and i1k are of same size in X dimension
 p.plot(i1k)
 #or
 p.plot(i1.X*10,i1.Y*i1.X**2)

Indexing dataArray/dataList and reducing
----------------------------------------
Basic **Slicing** and Indexing/Advanced Indexing/Slicing works as described at
`numpy <https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.indexing.html>`_

This means accessing parts of the dataArray/dataList by indexing with integers, boolean masks or arrays
to extract a subset of the data (returning a copy)

[A,B,C] in the following describes A dataList, B dataArray columns and C values in columns.

::

 i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
 # remove first 2 and last 2 datapoints in all dataArrays
 i6=i5[:,:,:2:-2]
 # remove first column and use 1,2,3 columns in all dataArrays
 i6=i5[:,1:4,:]
 # use each second elelemt in datalist and remove last 2 datapoints in all dataArrays
 i6=i5[::2,:,:-2]
 # You can loop over the dataArrays for individual usage.

**Reducing data** to a lower number of values is done by data.prune (see :py:class:`~.dataList` )

prune reduces e.g by 2000 points by averaging in intervalls to get 100 points.

::

 i7=js.dL(js.examples.datapath+'/a0_336.dat')
 # mean values in interval [0.1,4] with 100 points distributed on logscale
 i7_2=i7.prune(lower=0.1,upper=4,number=100,kind='log') #type='mean' is default

DataList can be **filtered** to use a subset eg to filter for q, temperature,.....

::

 i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
 i6=i5.filter(lambda a:a.q<2)

This demonstrates how to filter data values according to some rule. ::

 x=np.r_[0:10:0.5]
 D,A,q=0.45,0.99,1.2               # parameters
 rand=np.random.randn(len(x))      # the noise on the signal
 data=js.dA(np.vstack([x,np.exp(-q**2*D*x)+rand*0.05,x*0+0.05,rand])) # generate data with noise
 # select like this
 newdata=data[:,data[3]>0]         # take only positive noise in column 3
 newdata=data[:,data.X>2]          # X>2
 newdata=data[:,data.Y<0.9]        # Y<0.9

Fitting experimental data
-------------------------

For fitting we use methods from the scipy.optimize module that are incorporated in the .fit method.
.fit supports different fit algorithms (see dataList.fit Examples how to choose and about speed differences) :

- 'leastsq' (default) is a wrapper around MINPACK’s lmdif and lmder, which is a modification
  of the Levenberg-Marquardt algorithm.
  This is what you usually expect by "fitting" including error bars (and a covariance matrix for experts....).
- 'differential_evolution' is a global optimization method using iterative improving candidate solutions.
  In general it needs a large number of function calls but may find a global minimum and gives error bars.
- ‘BFGS’, ‘Nelder-Mead’, ..... other optimization methods.
  These are slower converging than 'leastsq' and give no error bars.
  Some require a gradient function ore more.
  They are more for advanced users if someone realy knows why using it.

First we need a model which can be defined in different ways.
See below or in :ref:`How to build simple models` for different ways.

Please avoid using lists as parameters as list are used to discriminate
between common parameters and individual fit parameters in dataList.

::

 import jscatter as js
 import numpy as np

 # read data
 data=js.dL(js.examples.datapath+'/polymer.dat')
 # merge equal Temperatures each measured with two detector distances
 data.mergeAttribut('Temp',limit=0.01,isort='X')

 # define model
 # q will get the X values from your data as numpy ndarray.
 def gCpower(q,I0,Rg,A,beta,bgr):
     """Model Gaussian chain  + power law and background"""
     gc=js.ff.gaussianChain(q=q,Rg=Rg)
     # add power law and background
     gc.Y=I0*gc.Y+A*q**beta+bgr
     # add attributes for later documentation, these are additional content of lastfit (see below)
     gc.A=A
     gc.I0=I0
     gc.bgr=bgr
     gc.beta=beta
     return gc

 data.makeErrPlot(yscale='l',xscale='l')    # additional errorplot with intermediate output
 data.setlimit(bgr=[0,1])                   # upper and lower soft limit

 # here we use individual parameter for all except a common beta ( no [] )
 # please try removing the [] and play with it :-)
 data.fit(model=gCpower,
          freepar={'I0':[0.1],'Rg':[3],'A':[1],'bgr':[0.01],'beta':-3},
          fixpar={},
          mapNames={'q':'X'},
          condition =lambda a:(a.X>0.05) & (a.X<4))

 # to fix a parameter move it to fixpar dict (bgr is automatically extended)
 data.fit(model=gCpower,
          freepar={'I0':[0.1],'Rg':[3],'A':[1]},
          fixpar={'bgr':[0.001, 0.0008, 0.0009],'beta':-4},
          mapNames={'q':'X'},
          condition =lambda a:(a.X>0.05) & (a.X<4))

 # result parameter and error (example)
 data.lastfit.Rg
 data.lastfit.Rg_err

 # save the fit result including parameters, errors and covariance matrix
 data.lastfit.save('polymer_fitDebye.dat')

Why Fits may fail
-----------------

If your fit fails it is most not an error of the fit algorithm.
Read the message at the end of the fit it gives a hint what happend.

- If your fit results in a not converging solution or maximum steps reached then its not a valid fit result.
  Decrease tolerance, increase maxstep or reduce number of parameter to get a valid result.
  Try more reasonable start parameters.
- Your model may have dependent parameters. Then the gradient cannot be evaluated.
  Think of it as a valley with a flat ground. Then you have a line as minimum but you ask for a point.
- Your starting parameters are way of and within the first try the algorithm finds no improvement.
  This may happen if you have a dominating function of high power and bad starting parameters.
  Choose better ones.
- You may run into a local minimum which also depends on the noise in your data.
  Try different start parameter or a global optimization method.
- Play with the starting parameters and get an idea how parameters influence your function.
  This helps to get an idea what goes wrong.

And finally :

- You have choosen the wrong model ( not correlated to your measurement),
  units are wrong by orders of magnitude, missing contributions, .....
  So read the docs of the models and maybe choose a better one.


Plot experimental data and fit result
-------------------------------------
::

 # plot data
 p=js.grace()
 p.plot(data,legend='measured data')
 p.xaxis(min=0.07,max=4,scale='l',label='Q / nm\S-1')
 p.yaxis(scale='l',label='I(Q) / a.u.')
 # plot the result of the fit
 p.plot(data.lastfit,symbol=0,line=[1,1,4],legend='fit Rg=$radiusOfGyration I0=$I0')
 p.legend()

 p1=js.grace()
 # Tempmean because of previous mergeAttribut; otherwise data.Temp
 p1.plot(data.Tempmean,data.lastfit.Rg,data.lastfit.Rg_err)
 p1.xaxis(label='Temperature / C')
 p1.yaxis(label='Rg / nm')

Save data
---------
jscatter saves files in a ASCII format including attributes that can be
reread including the attributes (See first example above and dataArray help).
In this way no information is lost. ::

 data.save('filename.dat')
 # later read them again
 data=js.dA('filename.dat')  # retrieves all attributes

If needed, the raw numpy array can be saved (see numpy.savetxt).
All attribute information is lost. ::

 np.savetxt('test.dat',data.array.T)





