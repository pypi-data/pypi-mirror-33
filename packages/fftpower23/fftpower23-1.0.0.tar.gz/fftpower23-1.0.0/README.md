fftpower23 package contains library to calculate Fast Foutrier Transformation.
Also it provides a set of functions to calculate commonly used sprectral characteristics (both single and mutual) for numerical series.

The main difference from the other simular packages that it provides FFT for the series those have length based both powers 2 and 3.
The exact formula for acceptable lenghts is 4*2**n*3**m; n,m >= 0.
Any particular length can be checked by calling function IsValidLength (lenght)
List of first 100 allowed numbers (number №100 = 373248) can be found in docs/first_100_allowed_lengths.txt

The source code successfully compiled and tested on both python 2.7.6 and python 3.4.3
Original algoryth has been rewritten to python from C++, C++ source code is available at https://bitbucket.org/VladimirPopov43/fft_cpp/src

Full public API with the example of usage can be found at docs/api_doc.txt

Sincerely yours,
Vladimir Popov, vladimir.popov@gmx.com
