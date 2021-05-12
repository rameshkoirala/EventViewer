#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2021 GRAND Collaboration
contact: rkoirala@nju.edu.cn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

class EventViewer:

    def __init__(self):
        self.geofile   = "/home/ramesh/Documents/GRAND/Data/GP300propsedLayout.dat"
        self.hdffile   = "/home/ramesh/Documents/GRAND/Data/Simulation/GP300Proton/GP300_Proton_0.251_74.8_2.58_1.hdf5"
        findex         = (re.search('GP300_', self.hdffile)).span()[0]  # index wher GP300_ starts in a filename.
        self.eventname = self.hdffile[findex:-5]
        # Get proposed geometry of GP300.
        #self.ID     = []    # Antenna name, eg: 'A0', 'A1', ..., 'A287'
        self.posx    = []    # x-coordinate of all antenna
        self.posy    = []    # y-coordinate of all antenna
        self.antpos  = np.column_stack((self.posx, self.posy))
        # Position and time of antennae that are hit. These arrays are arranged based on cronological order.
        self.hitX    = []
        self.hitY    = []
        self.hitT    = []
        #Quantities required to plot hits.
        self.Eweight = []
        self.palette_color    = []
        # Collection of all traces.
        self.trace_collection = {}

    def get_geometry(self):
        # Get proposed geometry of GP300.
        self.geo_df  = pd.read_csv(self.geofile, sep=" ", usecols=[1,2,3])
        #self.ID     = self.geo_df['ID']    # Antenna name, eg: 'A0', 'A1', ..., 'A287'
        self.posx    = self.geo_df['X']     # x-coordinate of all antenna
        self.posy    = self.geo_df['Y']     # y-coordinate of all antenna

    def get_data(self):
        astropy_antInfo   = GetAntennaInfo(self.hdffile, self.eventname)
        pd_antInfo        = pd.DataFrame(np.array(astropy_antInfo)) # astropy tables to pandas dataframe. Pandas dataframe is easier to work with.
        pd_antInfo['ID']  = pd_antInfo['ID'].str.decode('utf-8')    # b'A0' -->'A0', b'A1' --> 'A1' .....
        sorted_antInfo    = pd_antInfo.sort_values(by='T0')         # sort hits based on time.
        self.hitAnt       = sorted_antInfo['ID'].values
        self.hitT         = sorted_antInfo['T0'].values
        '''
        Position of Antennae changes based on shower core. This gives variable antannae position if taken from AntennaeInfo. 
        So antennae position is taken from the geometry based on Antennae ID.
        '''
        self.hitX     = [(self.geo_df[self.geo_df.ID.eq(ant_name)]['X']).values[0] for ant_name in self.hitAnt]
        self.hitY     = [(self.geo_df[self.geo_df.ID.eq(ant_name)]['Y']).values[0] for ant_name in self.hitAnt]
        self.palette_color = color_pallette(len(self.hitX))

    def update_plot(self):
        # Other required quantities that needs to change after changing input files.
        self.palette_color = color_pallette(len(self.hitX))

    def get_trace(self):
        weight = []
        tcurve = {}
        for i, ant_id in enumerate(self.hitAnt):
            efield   = GetAntennaEfield(self.hdffile, self.eventname, ant_id)
            Ex = efield[:,1]
            Ey = efield[:,2]
            Ez = efield[:,3]
            # calculate weight
            mEx = np.max(Ex)
            mEy = np.max(Ey)
            mEz = np.max(Ez)
            wt  =  np.sqrt(mEx*mEx + mEy*mEy + mEz*mEz)
            weight.append(wt)
            # plot traces
            curvex = hv.Curve(Ex, 'Trace Bins', 'Efield Trace').opts(color='r')
            curvey = hv.Curve(Ey, 'Trace Bins', 'Efield Trace').opts(color='b')
            curvez = hv.Curve(Ez, 'Trace Bins', 'Efield Trace').opts(color='g')
            curve  = curvex*curvey*curvez
            curve.opts(opts.Curve(show_grid=True))
            tcurve[i] = curve

        self.Eweight = weight
        self.trace_collection = tcurve
    
    def animate(self, event):
        '''
        Controls Play and Pause button. Plot hit by hit and pause time/1.e4 seconds between hits.
        '''
        if self.button.name == '▶ Play':
            self.button.name = '❚❚ Pause'
            # Check if the input file name has been changed. If changed start plotting the new event if 'Play' button is clicked.
            filename0  = self.input_file.filename
            if filename0!=None:
            	filename  = '../Data/Simulation/GP300Proton/' + filename0
            	if filename!=self.hdffile:
            		# if a new hdf file is provided, then start from the beginning.
            		self.hdffile       = filename
            		findex             = (re.search('GP300_', self.hdffile)).span()[0]  # index wher "GP300_" starts in a filename.
            		self.eventname     = self.hdffile[findex:-5]
            		self.get_data()    # get hitX, hitY, ..., tbins etc for a new input hdf file.
            		self.get_trace()   # get electric field traces from a new hits.

            t, t_last = min(self.hitT), max(self.hitT)
            tdiff     = np.diff(self.hitT)
            indx      = 0
            # loop over all hits and send data via pipe to plot one by one. Pause in between hits.
            while indx<len(self.hitT):
            	t    = self.hitT[indx]
            	if indx==0:
            		time.sleep(0.5)                        # give half a second before plotting the first hit.
            	else:
            		time.sleep(tdiff[indx-1]/1.e4)
            	indx+= 1

            	mask = self.hitT<=t                        # Mask to select all hits before a given time.
            	x    = np.array(self.hitX)[mask]           # select x-coordinate of hit antenna before a given time.
            	y    = np.array(self.hitY)[mask]           # select y-coordinate of hit antenna before a given time.
            	t    = np.array(self.hitT)[mask]           # select list of time before the boundary time.
            	wt   = np.array(self.Eweight)[mask]        # Weight based on electric field strength. This is an adhoc weight and has no physical meaning.
            	color = np.array(self.palette_color)[mask] # select color from a palette that was created based on time of hit.
            	self.stream_hits.send((x,y,t,wt,color))
            # After all hits are plotted, change the 'Play' button to 'Pause'.
            self.button.name = '▶ Play'
    		
    def plot_hits(self,data):
        """
        This function controls evolution of hit on antenna. Color represents the time of hit and 
        the size of circle represents the size of signal on antennae. But the size of circle and
        the strength of electric field/voltage on antennae are not directly related.
        
        Hits to be plotted are appended one by one. Gap between hits are maintained. As the 
        time progress, number of hits keeps on adding until all hits from that event are included. 
        Note that antennae information provided arealready sorted based on time of hit.
        """
        # "data" is sent here from "animate()".
        x = data[0]
        y = data[1]
        t = data[2]
        wt= data[3]
        color = data[4]
        kdims = ['X', 'Y']
        vdims = ['Eweight', 'T', 'color']
        if len(x)==0:
        	fig = hv.Points([], kdims=kdims, vdims=vdims)
        	fig.opts(opts.Points(width=700, height=650, tools=['hover']))
        else:
        	pd_data = pd.DataFrame(data={'X':x,        # create a pandas dataframe.
	                                     'Y':y, 
	                                     'Eweight':wt, 
	                                     'T':t,
	                                     'color':color})

	        ds = hv.Dataset(pd_data)                   # create a holoview dataset from pandas dataframe.
	        '''This is the part where hits are plotted. This function is called many times and in each call number of hits are added until all hits are include.'''
	        fig = hv.Points(ds, kdims=kdims, vdims=vdims)
	        '''Add options to the plot.'''
	        fig.opts(opts.Points(width=700, height=650,
	                             size=np.log(dim('Eweight'))*4.5,
	                             marker='circle',
	                             color='color',
	                             alpha=0.9,
	                             tools=['hover']))
        return fig

    def pick_trace(self, index):
        '''
        Electric field traces from all hit antenna are collected. This function picks traces from collected traces
        for a particular antenna for plotting when clicked on that antenna. Traces will be plotted only for antenna 
        that are hit.
        '''
        if not index:
            curve = hv.Curve([], 'Trace Bins', 'Efield Trace')*hv.Curve([], 'Trace Bins', 'Efield Trace')
            return curve
        antEtrace = self.trace_collection[index[0]]
        antEtrace.opts(opts.Curve(width=450, height=300, line_width=1, tools=['hover']))
        return antEtrace

    def view(self):

        self.input_file = pn.widgets.FileInput(accept='.hdf5')
        self.get_geometry()# get updated position of antennae, (i.e. posx, posy)
        self.get_data()    # get updated hitAnt, hitX, hitY, and hitT
        self.get_trace()   # get updated electric field traces.

        # Plot detector geometry with all antennae position.
        antpos        = np.column_stack((self.posx, self.posy))
        antposplot    = hv.Points(antpos)
        antposplot.opts(opts.Points(color='black',
                                    fill_color='black',
                                    alpha=0.2,
                                    fill_alpha=0.2,
                                    marker='circle',
                                    size=8,
                                    tools=['hover'],
                                    fontsize=20,
                                    xlabel='North [m]', 
                                    ylabel='West[m]',
                                    toolbar='above'
                                ))

        # --------- Play/Pause botton. ------------------#
        self.palette_color = color_pallette(len(self.hitX))
        self.button        = pn.widgets.Button(name='▶ Play', width=80, align='end')
        self.button.on_click(self.animate)

        # --------- Dynamically updating plot starts here ------------#
        self.stream_hits  = hv.streams.Pipe(data=[[],[],[],[],[]])
        dmap_hits_plot    = hv.DynamicMap(self.plot_hits, streams=[self.stream_hits])
        self.dmap         = antposplot*dmap_hits_plot                    # plot GP300 geometry and dynamic map of hits on the same canvas.
        dmap_hits_plot.opts(opts.Points(tools=['tap', 'hover']))      # tap hits antenna to plot its electric field traces.
        
        # --------------------------------------------------------------------
        stream_click      = hv.streams.Selection1D(source=dmap_hits_plot, index=[0])
        self.antEtrace    = hv.DynamicMap(self.pick_trace, 
                                  kdims=[], 
                                  streams=[stream_click]).opts(show_grid=True)

        # -----Placeholder plot -----------
        self.placeholder  = hv.Curve([]).opts(width=450, height=300)

        # panel is used to arange plots for final viewing.
        final_plot        = pn.Column(pn.Row(self.button, self.input_file),
                               pn.Row(self.dmap, pn.Column(self.antEtrace, self.placeholder))
                           	)

        final_plot.show()

if __name__=='__main__':

    import argparse          # argparse is a better version of OptionParser.
    import re
    import time
    import numpy as np
    import pandas as pd    
    # http://holoviews.org/getting_started/index.html
    import panel as pn
    import holoviews as hv
    from holoviews import opts, dim
    #from holoviews.streams import Selection1D
    from hdf5fileinout import GetAntennaInfo, GetAntennaEfield #Written by Matias Tueros.
    from bokeh.palettes import inferno #, Magma, Inferno, Inferno256, Plasma, Viridis, Cividis, Spectral

    color_pallette = inferno

    hv.extension('bokeh')

    # =============================================================================
    parser = argparse.ArgumentParser()
    parser.add_argument("--gf",
              default="/home/ramesh/Documents/GRAND/Data/GP300propsedLayout.dat", 
              help="Geometry of antenna in GP300.")
    parser.add_argument("--hf",
              default="/home/ramesh/Documents/GRAND/Data/Simulation/GP300Proton/GP300_Proton_0.251_74.8_2.58_1.hdf5", 
              help="Name of one or many hdf5 file where experimental or simulation data are stored.")

    args        = parser.parse_args()

    eventviewer = EventViewer()
    eventviewer.view()