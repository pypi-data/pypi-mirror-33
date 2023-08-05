import os
import sys
import math
import numpy as np
from pylab import exp

from bisect import bisect_left

from scipy import interpolate
import neutron_detector_eff_functions.B10 as B10
import neutron_detector_eff_functions.Aluminium as Aluminium
import neutron_detector_eff_functions.efftools as efftools
import neutron_detector_eff_functions.Blade as Blade
import copy
import json


class Detector:

    def __init__(self, name='Detector', angle=90, threshold=100, single=False):
        self.converter = B10.B10()
        self.name = name
        self.wavelength = []
        self.angle = angle
        self.threshold = threshold
        self.single = single
        self.metadata = {}
        self.blades = []
        self.converterConfiguration = ''


    def calculate_eff(self):
        assert len(self.blades) >= 1
        assert len(self.wavelength) >= 1
        ranges = self.calculate_ranges()
        sigma = self.calculate_sigma()
        varargin = 1
        result = []
        if self.single:
            print ('Boron single layer calculation ')
            result=[[0,0],[0,0]]
            c=0
            for s in sigma:
                resultTemp = efftools.efficiency4boron(self.blades[0].backscatter, ranges[0], ranges[1], ranges[2], ranges[3], s)
                result[0][0] = result[0][0] + resultTemp[1][0]*self.wavelength[c][1]*0.01
                result[1][0] = result[1][0] + resultTemp[2][0]*self.wavelength[c][1]*0.01
                c+=1
        else:
            print ('Boron multi-blade double coated calculation ')
            thickness = []
            for b in self.blades:
               thickness.append(b.backscatter)
            resultpoli = []
            #result = efftools.data_samethick_vs_thickandnb_depth(sigma, ranges, self.blades)
            result=[[],0]
            for n in range(0, len(self.blades)):
                result[0].append([0, 0])
            for s in sigma:
                resultpoli.append(efftools.mgeff_depth_profile(thickness, ranges, s, varargin))
            for i, r in enumerate(resultpoli):
                for j, ewz in enumerate(resultpoli[i][0]):
                    result[0][j][0] = result[0][j][0] + ewz[0]*self.wavelength[i][1]*0.01
                result[1] = result[1] + resultpoli[i][1]*self.wavelength[i][1]*0.01
        return result

    def calculate_ranges(self):
        """calculates range of 4 particles given a threshold and configuration of B10.

        Returns:
        	    r[1,4]: r(1,1)=ralpha_94;
                 r(1,2)=rLi_94;
                 r(1,3)=ralpha_06;
                 r(1,4)=rLi_06;

            ranges in um

        ..  Original source in Matlab: https://bitbucket.org/europeanspallationsource/dg_matlabborontools/src/bcbac538ad10d074c5150a228847efc2e0269e0d/B10tools/rangesMAT.m?at=default&fileviewer=file-view-default

        """
        return self.converter.ranges(self.threshold, self.converterConfiguration)

    def calculate_sigma(self):
        """calculates sigma equivalent of Boron depending on sigma and angle
               ..  Original source in Matlab: https://bitbucket.org/europeanspallationsource/dg_matlabborontools/src/bcbac538ad10d074c5150a228847efc2e0269e0d/B10tools/macroB10sigma.m?at=default&fileviewer=file-view-default

               """
        return self.converter.full_sigma_calculation(self.wavelength, self.angle)

    def plot_blade_figure(self, eff, figure):
        """plots the efficiency of all blades,

        Returns:
        	plotted figure

            reference: figure 3.14 On Francesco's Thesis
        """
        if eff is None:
            eff = self.calculate_eff()
        ax = figure.add_subplot(111)
        ax.set_xlabel('Blade number')
        ax.set_ylabel('Blade efficiency %')
      #  ax.set_ylim([0, (eff[1] * 100 + 1)])
        ax.set_xlim([0, len(eff[0]) + 1])
        ax.plot(0, 0)
        ax.plot(0, len(eff[0]) + 1)
        # ax.plot(nb + 1, 0)
        meta = []
        nlist = []
        for n in range(0, len(eff[0])):
            # Note that the plot displayed is the backscattering thickness
            ax.plot(n + 1, eff[0][n][0] * 100, 'o', color='red')
            meta.append(eff[0][n][0] * 100)
            nlist.append(n+1)
        self.metadata.update({'effvsdepth': [nlist,meta]})
        ax.grid(True)
        return ax

    def plot_blade_meta(self, eff):
        """plots the efficiency of all blades,

        Returns:
        	plotted figure

            reference: figure 3.14 On Francesco's Thesis
        """
        if eff is None:
            eff = self.calculate_eff()
        # ax.plot(nb + 1, 0)
        meta = []
        nlist = []
        for n in range(0, len(eff[0])):
            # Note that the plot displayed is the backscattering thickness
            meta.append(eff[0][n][0] * 100)
            nlist.append(n+1)
        self.metadata.update({'effvsdepth': [nlist,meta]})


    def plot_blade_figure_single(self, result, figure):
        """plots the efficiency of a single layer,

        Returns:
        	plotted figure\
        """
        ax = figure.add_subplot(111)
        ax.set_xlabel('Blade Number')
        ax.set_ylabel('Blade efficiency (%)')
        ax.set_ylim([0, (result[1][0] * 100 + 1)])
        ax.set_xlim([0, 2] )
        ax.plot(0, 0)
        ax.plot(0, len(result[0]) + 1)
        # ax.plot(nb + 1, 0)
        ax.plot(1, result[0][0] * 100, 'o', label=" BS", color='red')
        ax.plot(1, result[1][0] * 100, 'o', label=" TS", color='b')
        ax.legend(numpoints=1)
        ax.grid(True)
        return ax



    def plot_thick_vs_eff_meta(self):
        """plots the efficiency function for a set of thicknesses,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.12 On Francesco's Thesis
        """
        sigma = self.calculate_sigma()
        sigmalist = []
        c = 0
        for s in sigma:
            sigmalist.append([s, self.wavelength[c][1]])
            c += 1
        ranges = self.calculate_ranges()
        blades = self.blades
        result = self.calculate_eff()

        if self.single:
            thickVsEff = efftools.metadata_samethick_vs_thickandnb_single(sigmalist, ranges, len(blades))
        else:
            thickVsEff = efftools.metadata_samethick_vs_thickandnb(sigmalist, ranges, len(blades))
            self.metadata.update({'thickVsEff': thickVsEff})


    def plot_wave_vs_eff(self,sigmaeq, sigmalist, ranges, blades, result, wavelength, figure):
        """plots the efficiency for a set of wavelengths,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.13 On Francesco's Thesis
        """
        if sigmaeq == None:
            sigmaeq = self.calculate_sigma()
        if ranges == None:
            sigmaeq = self.calculate_ranges()
        if self.single:
            y = efftools.metadata_singleLayer_vs_wave(sigmaeq, blades[0].backscatter, ranges, len(blades))
        else:
            y = efftools.metadata_diffthick_vs_wave(sigmaeq, blades, ranges, len(blades))
        cx = figure.add_subplot(111)
        self.metadata.update({'effVsWave': [sigmalist, y]})
        cx.plot(sigmalist, y, color='g')
        if self.single:
            cx.plot([wavelength[0][0], wavelength[0][0]], [0, result[1][0]], '--',
                    color='k')
            cx.plot([0, wavelength[0][0]], [result[1][0], result[1][0]], '--', color='k')
        else:
            cx.plot([wavelength[0][0], wavelength[0][0]], [0, result[1]], '--',
                    color='k')
            cx.plot([0, wavelength[0][0]], [result[1], result[1]], '--', color='k')
        cx.grid(True)
        cx.set_xlabel('Neutron wavelength (Angstrom)')
        cx.set_ylabel('Detector efficiency (%)')
      #  ticks = cx.get_yticks() * 100
       # cx.set_yticklabels(ticks)
        return cx



    def plot_eff_vs_wave_meta(self):
        """plots the efficiency for a set of wavelengths,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.13 On Francesco's Thesis
        """
        sigmalist = np.arange(0.0011, 20, 0.1)
        sigmaeq = []
        for sigma in sigmalist:
            # transformation for meeting requirements of functions
            sigma = [[sigma], ]
            sigmaeq.append(B10.B10().full_sigma_calculation(sigma, self.angle))
        ranges = self.calculate_ranges()
        blades = self.blades
        result = self.calculate_eff()
        wavelength = self.wavelength
        y = efftools.metadata_diffthick_vs_wave(sigmaeq, blades, ranges, len(blades))
        self.metadata.update({'effVsWave': [sigmalist, y]})


    def optimize_thickness_same(self):
        """sets the thickness of all blades to the most optimal for all the blades with same thickness.
        """
        #meta = self.metadata.get('thickVsEff')
        sigma = self.calculate_sigma()
        sigmalist =[]
        c = 0
        for s in sigma:
            sigmalist.append([s, self.wavelength[c][1]])
            c += 1
        meta = efftools.metadata_samethick_vs_thickandnb(sigmalist, self.calculate_ranges(), len(self.blades))
        max = np.array(meta[1]).argmax()
        c = 0
        max = meta[0][max]
        nb = len(self.blades)
        for b in self.blades:
            b.backscatter = max
            self.blades[c] = b
            c += 1

    def optimize_thickness_diff(self):
        """sets the thickness of all blades to the most optimal with different thickness
        """
        thickrange = np.arange(0.00, 5, 0.01)
        wavelength = self.wavelength
        # check polichromatic wavelength
        if len(self.wavelength) > 1:
            print ('optimization for polichromatic wavelength')
            self.wavelength = [[self.calculate_barycenter(), 100]]
        sigma = self.calculate_sigma()
        sigma = sigma[0]
        ranges = self.calculate_ranges()
        eff1 = []
        effopt = [None] * (len(self.blades))
        alpha = 0
        dopt = [None] * (len(self.blades))
        for t in thickrange:
            temp = efftools.efficparam(t,sigma,ranges,1)
            eff1.append(temp[3])  #no substrate
        for i in range(len(self.blades)-1, -1, -1):
            tempeff = []
            for j, t in enumerate(thickrange):
                tempeff.append(eff1[j] + (exp(((-1)*(2*thickrange[j]*sigma))))*alpha)
            effopt[i] = max(tempeff)
            alpha = effopt[i]
            dopt[i] = thickrange[np.array(tempeff).argmax()]
            self.blades[i].backscatter = dopt[i]
        totaleff = sum(effopt)
        if len(self.wavelength) > 1:
            self.wavelength = wavelength


    @staticmethod
    def build_detector(nb, converterThickness, substrateThickness, wavelength, angle, threshold, single, converter):

        bladelist = []
        blade = Blade.Blade(converterThickness,converterThickness,substrateThickness,0)
        if single:
            nb = 1
        for x in range(0,nb):
            bladelist.append(copy.deepcopy(blade))
        detector = Detector()
        #TODO check existing converter
        detector.converterConfiguration = converter
        detector.blades = bladelist
        detector.wavelength = wavelength
        detector.angle = angle
        detector.threshold = threshold
        detector.single = single
        return detector

    def calculate_barycenter(self):
        bari = 0
        weight = 0
        for w in self.wavelength:
            bari=bari+(w[0]*w[1])
            weight+=w[0]
        return bari/100

    def calculate_varargin(self):
        thick = self.blades[0].substrate
        varargin = Aluminium.aluminium(thick,self.wavelength,self.angle)
        return varargin[0]


    @staticmethod
    def json_parser(path):
        try:
            with open(path) as data_file:
                data = json.load(data_file)
            wave =[]
            for w in data.get('wavelength'):
                wave.append([w.get('angstrom'), w.get('%')])
            detector = Detector.build_detector(len(data.get('blades')),data.get('blades')[0].get('backscatter'),data.get('blades')[0].get('substrate'),wave, data.get('angle'), data.get('threshold'), data.get('single'), data.get('converterConfiguration'))
            # Access data
            return detector
        except (ValueError, KeyError, TypeError):
            print ("JSON format error")

    def to_json(self):
        d = {}
        d["name"] = self.name
        d["converterConfiguration"] = self.converterConfiguration
        d["angle"] = self.angle
        d["threshold"] = self.threshold
        blades = []
        for b in self.blades:
            bdict = {}
            bdict["backscatter"] = b.backscatter
            bdict["transmission"] = b.transmission
            bdict["substrate"] = b.substrate
            bdict["inclination"] = b.inclination
            blades.append(bdict)
        wavelength = []
        for w in self.wavelength:
            wdict = {}
            wdict["%"] = w[1]
            wdict["angstrom"] = w[0]
            wavelength.append(wdict)
        d["blades"] = blades
        d["single"] = self.single
        d["wavelength"] = wavelength
        return d


if __name__ == '__main__':
   #Detector.json_parser('/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports/detector1.json')
   detector = Detector.detector(15,1,0,[[10,100]], 90, 100)
   detector.optimize_thickness_diff()
