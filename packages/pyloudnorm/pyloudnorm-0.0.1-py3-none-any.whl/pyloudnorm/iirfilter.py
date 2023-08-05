class IIRfilter():
    """ IIR Filter object to pre-filtering
    
    This class allows for the generation of various IIR filters
	in order to apply different frequency weighting to audio data
	before measuring the loudness. 

    Parameters
    ----------
    G : float
        Gain of the filter in dB.
    Q : float
        Q of the filter.
    fc : float
        Center frequency of the shelf in Hz.
    rate : float
        Sampling rate in Hz.
    filter_type: str
        Shape of the filter.
    """

    def __init__(self, G, Q, fc, rate, filter_type):
        self.G  = G
        self.Q  = Q
        self.fc = fc
        self.rate = rate
        self.filter_type = filter_type
        self.b, self.a = self.generate_filter_coefficients()

    def __str__(self):
        info = ("""
        {type}
        ----------------------
        Gain         = {G} dB
        Q factor     = {Q} 
        Center freq. = {fc} Hz
        Sample rate  = {rate} Hz
        ----------------------
        b0 = {_b0}
        b1 = {_b1}
        b2 = {_b2}
        a0 = {_a0}
        a1 = {_a1}
        a2 = {_a2}
        ----------------------
        """).format(type=self.valid_types[self.filter_type], 
        G=self.G, Q=self.Q, fc=self.fc, rate=self.rate, 
        _b0=self.b[0], _b1=self.b[1], _b2=self.b[2], 
        _a0=self.a[0], _a1=self.a[1], _a2=self.a[2])

        return dedent(info)

    def generate_filter_coefficients(self):
        """ Generates biquad filter coefficients using instance filter parameters. 

        This method is called whenever an IIRFilter is instantiated and then sets
        the coefficients for the filter instance. NOTE: Changing the IIRFilter 
        instance filter paramters will not update the filter coefficents unless
        this method is called after the modification. 

        Returns
        -------
        b : ndarray
            Numerator filter coefficients stored as [b0, b1, b2]
        a : ndarray
            Denominator filter coefficients stored as [a0, a1, a2]
        """
        A  = 10**(self.G/40.0)
        w0 = 2.0 * np.pi * (self.fc / self.rate)
        alpha = np.sin(w0) / (2.0 * self.Q)

        if self.filter_type == 'high_shelf':
            b0 =      A * ( (A+1) + (A-1) * np.cos(w0) + 2 * np.sqrt(A) * alpha )
            b1 = -2 * A * ( (A-1) + (A+1) * np.cos(w0)                          )
            b2 =      A * ( (A+1) + (A-1) * np.cos(w0) - 2 * np.sqrt(A) * alpha )
            a0 =            (A+1) - (A-1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 =      2 * ( (A-1) - (A+1) * np.cos(w0)                          )
            a2 =            (A+1) - (A-1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        elif self.filter_type == "peaking":
            b0 =   1 + alpha * A
            b1 =  -2 * np.cos(w0)
            b2 =   1 - alpha * A
            a0 =   1 + alpha / A
            a1 =  -2 * np.cos(w0)
            a2 =   1 - alpha / A
        elif self.filter_type == 'high_pass':
            b0 =  (1 + np.cos(w0))/2
            b1 = -(1 + np.cos(w0))
            b2 =  (1 + np.cos(w0))/2
            a0 =   1 + alpha
            a1 =  -2 * np.cos(w0)
            a2 =   1 - alpha
        else:
            raise ValueError("Invalid filter typer", self.filter_type)

        return np.array([b0, b1, b2])/a0, np.array([a0, a1, a2])/a0

    def plot_magnitude(self):
        """ Plot the magnitude response of the filter.

        This method is provided for debuging and validation of the 
        generated filter coefficients. These plots should match those
        as outlined in the ITU-R 1770-4 standard. 

        """
        fig = plt.figure(figsize=(9,9))
        w, h = scipy.signal.freqz(self.b, self.a, worN=8000)
        plt.semilogx((self.rate * 0.5 / np.pi) * w, 20 * np.log10(abs(h)))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Gain [dB]')
        if self.filter_type == 'high_shelf':
            plt.title('Pre-filter 1: High Shelving Filter')
            plt.xlim([20, 20000])
            plt.ylim([-10,10])
            plt.grid(True, which='both')
            ax = plt.axes()
            ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
        else:
            plt.title('Pre-filter 2: Highpass Filter')
            plt.xlim([10, 20000])
            plt.ylim([-30,5])
            plt.grid(True, which='both')
            ax = plt.axes()
            ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        plt.show()

    def apply_filter(self, data):
        """ Apply the IIR filter to an input signal.

        Params
        -------
        data : ndarrary
            Input audio data.

        Returns
        -------
        filtered_signal : ndarray
            Filtered input audio.
        """
        return scipy.signal.lfilter(self.b, self.a, data)
      