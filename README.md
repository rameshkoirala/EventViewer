Using "holoviews" package to create this event display. It uses 'bokeh' and 'matplotlib' as a base for visualization and creating widget.

Needs python 3.6 or higher.

Install holoviews. All required dependencies should automatically be installed, including 'bokeh'.

  $ pip3 install "holoviews[all]"    # For more info: http://holoviews.org/
  
  
After installing holoviews, add $HOME/.local/bin in the PATH so that packages installed there can be accessed.

  $ cd ~
  
  $ subl .bashrc      (or .bash_profile)
  
Inside .bashrc (or .bash_profile), add the following line

    export PATH=$HOME/.local/bin:$PATH


If above mentioned process fails to install bokeh, then install it by

  $ pip3 install bokeh 	# For more inof: https://docs.bokeh.org/en/latest/


After successfully installing "holoviews", install event-viewer as follows.

  $ cd <path/to/event-viwer/direcotry/>
  
  $ mkdir EventViewer    # Name of the directory can be anything you choose.
  
  $ cd EventViewer
  
  $ git clone https://github.com/rameshkoirala/EventViewer.git
  
After successfully installing EventViewer, you can run the package by

  $ python3 event_viewer.py --datadir <path>
	
  $ python3 event_viewer.py --datadir <path> --hf <filename> --gf <geometry filename>

	
----------- MIT License -------------
	
Copyright (c) 2021 GRAND Collaboration
	
contact: rkoirala@nju.edu.cn

	
Permission is hereby granted, free of charge, to any person obtaining a copy of this 
	
software and associated documentation files (the "Software"), to deal in the Software 
	
without restriction, including without limitation the rights to use, copy, modify, merge, 
	
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons 
	
to whom the Software is furnished to do so, subject to the following conditions:
	

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. 
	

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
	
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
	
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
	
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
	
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
	
DEALINGS IN THE SOFTWARE.
