# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 18:33:31 2021

@author: Falk Schneider @faldalf
"""
# Try to visualise phasor transform of an exponential decay (emulating a TCSPC curve)
# Just a toy script for visualisation purposes.
#
# Trying to make it a bit interactive .
# Allwos tuning one or two lifetimes and their amplitude.
# Laser repetition fixed to 80 MHz.
#
# FS @faldalf 04/08/2021
#
# Update 26/10/2021
# Trying to get the point directly on the circle
# - created makeExponential2 to wrap values around, make it periodic -> does not have a huge effect but adding a fake component
# - for visualisation it works to just set the circle radius to 0.49 (sort of cheating but does the trick )


#%% Imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

#%% Functions

def makeExponential (rep_rate, num_tcspc_chan, tau1, tau2=0, A2=0):
    #Simulate an exponential decay (you could include noise, background or more components)
    max_bin = 1/rep_rate *10**9 # converts to ns
    A1 = 1- A2
    x = np.linspace (0, max_bin, num_tcspc_chan)
    y = A1 * np.exp (-x/tau1)+ A2 * np.exp (-x/tau2)
 
   
    return x, y

def makeExponential2 (rep_rate, num_tcspc_chan, tau1, tau2=0, A2=0):
    #Simulate an exponential decay (you could include noise, background or more components)
    # Updated version that wraps long decays around the boundary by calculating a 25 ns decay
    # Does not have a huge effect. 
    # In fact ... introduces an artefact. 
    max_bin = 1/rep_rate *10**9 # converts to ns
    A1 = 1- A2
    x = np.linspace (0, 2*max_bin, num_tcspc_chan)
    y2 = A1 * np.exp (-x/tau1)+ A2 * np.exp (-x/tau2)
 
    y = y2[:int(len(y2)/2)]
    y = y + y2[int(len(y2)/2):]
    
    x = x[:int(len(y2)/2)]
    y [y < 0.000001] = 0 # ensure values go to
    
    
    return x, y

def calcPhasor1 (x,y,rep_rate):
# based on http://www.iss.com/resources/pdf/technotes/FLIM_Using_Phasor_Plots.pdf
# equation 8
# Using phasor transform of the simulated data data 
# Alternatively, one could use the analytical solution for known lifetimes:
# eq 9/10: Vallmitjana, A. et al. Resolution of 4 components in the same pixel in FLIM images using the phasor approach. Methods Appl. Fluoresc. 8, (2020).
    
    omega = np.pi * 2 * rep_rate *10**-9 # angular repetition rate
    n = 1 # harmonic number Usually 1,2,3
    # Calculate phasor coordinates:
    G_n = np.sum (y*np.cos(n*(omega)*x)) / np.sum (y)
    S_n = np.sum (y*np.sin(n*(omega)*x) / np.sum (y))
    
    return G_n, S_n


def update(val):
    # Update slider values: Read new values, recalculate TCSPC and Phasor
    tau1_new = s_tau1.val
    tau2_new = s_tau2.val
    A2_new = s_A2.val
    
    x_new, y_new = makeExponential (rep_rate, num_tcspc_chan, tau1_new, tau2_new, A2_new)
    G_n, S_n = calcPhasor1 (x_new,y_new, rep_rate)
    tcspc_plot.set_data(x_new,y_new)
    phasor_plot.set_data (G_n, S_n)
    fig.canvas.draw_idle()

#%% The actual script

# Let's generate a TCSPC decay curve
rep_rate = 80 * 10**6 # Repetition rate in Hz
num_tcspc_chan = 100 # Number of TCSPC channels, number of points on the exponential decay
tau1 = 0.1 # Lifetime 1
tau2 = 0.1 # Lifetime 2
A2 = 0.0 # Amplitude Lifetime 2

# Synthetic data
x, y = makeExponential (rep_rate, num_tcspc_chan, tau1, tau2, A2)

# Calculate Phasor Transform
G_n1, S_n1 = calcPhasor1 (x,y, rep_rate)

# Plot da shit
fig, axes = plt.subplots (ncols = 2, nrows = 1, figsize = (12,7))
plt.subplots_adjust(left=0.2, bottom=0.4)
ax0, ax1 = axes.flatten() 

tcspc_plot, = ax0.plot (x,y,'o')
ax0.set_xlabel ('Photon Arrival Time (ns)')
ax0.set_ylabel ('Normalised Counts (a.u.)')
ax0.set_title ('TCSPC Decay Curve')

phasor_plot, = ax1.plot (G_n1, S_n1, 'o', markersize=10)
my_circle = plt.Circle((0.5, 0), radius=0.49, edgecolor='b', facecolor='None') # Plot unity circle for reference
axes[1].add_patch (my_circle)
ax1.set_xlim ([0,1])
ax1.set_ylim ([0,1])
ax1.set_xlabel ('G')
ax1.set_ylabel ('S')
ax1.set_title ('Phasor Transform')
ax1.legend (['Phasor value',  'Unity circle'])

# The interactive part
# Add sliders to change values dynamically
axcolor = 'lightgoldenrodyellow'
ax_tau1 = plt.axes([0.25, 0.3, 0.65, 0.03], facecolor=axcolor)
ax_tau2 = plt.axes([0.25, 0.2, 0.65, 0.03], facecolor=axcolor)
ax_A2 = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
# Initialise sliders
s_tau1 = Slider(ax_tau1, 'Lifetime tau1 (ns)', 0.1, 8.0, valinit=tau1, valstep=0.1)
s_tau2 = Slider(ax_tau2, 'Lifetime tau2 (ns)', 0.1, 8.0, valinit=tau2, valstep = 0.1)
s_A2 = Slider(ax_A2, 'Amplitude tau2', 0.0, 1.0, valinit=0, valstep = 0.05)
# Update values
s_tau1.on_changed(update)
s_tau2.on_changed(update)
s_A2.on_changed(update)














