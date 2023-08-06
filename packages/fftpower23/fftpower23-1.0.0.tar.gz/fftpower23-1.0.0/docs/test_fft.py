import csv
import fftpower23

data_x = []
data_y = []

fh = open ("input.csv", "r")

for r in csv.reader (fh) :
    x, y = r
    data_x.append (float(x))
    data_y.append (float(y))
fh.close()

co = fftpower23.FastFourierTransformer (len(data_x))

if not co.IsValidObject () :
    print ("Incorrect length of data: ", len(data_x))
else :
    print (data_x)
    print (data_y)

    print ("FX")
    flag, FX_data = co.CalculateFourierCoefficients (data_x)
    print (FX_data)

    print ("FY")
    flag, FY_data = co.CalculateFourierCoefficients (data_y)
    print (FY_data)

    print ("FXc, FXs")
    flag, FXc_data, FXs_data = co.BuildFullCosSinCoeffs (FX_data)
    print (FXc_data)
    print (FXs_data)

    print ("FYc, FYs")
    flag, FYc_data, FYs_data = co.BuildFullCosSinCoeffs (FY_data)
    print (FYc_data)
    print (FYs_data)

    print ("x, reversed x")
    flag, X_Reverse = co.ReverseFourierTransformation (FXc_data, FXs_data)
    print (data_x)
    print (X_Reverse)

    print ("y, reversed y")
    flag, Y_Reverse = co.ReverseFourierTransformation_by_coeffs (FY_data)
    print (data_y)
    print (Y_Reverse)

    print ("X : Amplitude, Phase")
    flag, X_Ampl, X_Phase = co.BuildAmplitudeSpectrum (FX_data)
    print (X_Ampl)
    print (X_Phase)

    print ("Y : Amplitude, Phase")
    flag, Y_Ampl, Y_Phase = co.BuildAmplitudeSpectrum (FY_data)
    print (Y_Ampl)
    print (Y_Phase)

    print ("XY cross coeffs")
    flag, XY_cross_coeffs = co.BuildCrossFourierCoefficients (FX_data, FY_data)
    print (XY_cross_coeffs)

    print ("XY covar")
    flag, XY_covar = co.ReverseFourierTransformation_by_coeffs (XY_cross_coeffs)
    print (XY_covar)

    print ("XY cross: Ampl, Phase")
    flag, XY_Ampl, XY_Phase = co.BuildAmplitudeSpectrum (XY_cross_coeffs)
    print (XY_Ampl)
    print (XY_Phase)

    fh = open ("output.csv", "w")
    w = csv.writer (fh)

    w.writerow (("x", "y", "FX", "XC", "XS", "FY", "YC", "YS", "xr", "yr", "FXY", "covar"))

    for i in range (co.GetSize()) :
        w.writerow ((data_x[i], data_y[i], FX_data[i], FXc_data[i], FXs_data[i], \
                     FY_data[i], FYc_data[i], FYs_data[i], \
                     X_Reverse[i], Y_Reverse[i], XY_cross_coeffs[i], XY_covar[i]))
    w.writerow (",")

    w.writerow (("Ax", "Phx", "Ay", "PhY", "Axy", "Phxy"))
    for i in range (co.GetAmplSize()) :
        w.writerow ((X_Ampl[i], X_Phase[i], Y_Ampl[i], Y_Phase[i], \
                     XY_Ampl[i], XY_Phase[i]))
    fh.close

print ("Done")
