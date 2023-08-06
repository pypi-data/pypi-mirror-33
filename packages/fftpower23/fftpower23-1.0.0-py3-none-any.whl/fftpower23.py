import math
import array

def IsValidLength (dim) :
    
    if type(dim) != int : return False
    
    if (dim < 4) or (dim%4 > 0) : return False

    dim /= 4
    
    while dim > 1 :
        
        if dim%3 == 0 : dim //= 3
        elif dim%2 == 0 : dim //= 2
        else : return False
    
    return True

class FastFourierTransformer (object):
#private:
#    FastFourierTransformer (int length);
#    void recursive_fast_fourier (const double *data, double *f_x, int n, int step);
#public:
#    const double *SinTbl;
#    bool IsValidObject () const;
#    int GetSize () const;
#    int GetAmpleSize () const;
#    bool CalculateFourierCoefficients (const double *p_data, double *p_FX_coeffs);
#    bool BuildFullCosSinCoeffs (const double *p_FX_coeffs, double *p_cos_coeffs, double *p_sin_coeffs) const;
#    bool ReverseFourierTransformation (const double *p_cos_coeffs, const double *p_sin_coeffs, double *p_data);
#    bool ReverseFourierTransformation_by_coeffs (const double *p_FX_coeffs, double *p_data);
#    bool BuildAmplitudeSpectrum (const double *p_FX_coeffs, double *p_ampl, double *p_phase) const;
#    bool BuildCrossFourierCoefficients (const double *p_FX_coeffs, const double *p_FY_coeffs, double *p_XY_coeffs) const;

    __len = 0
    
    def IsValidObject (self) : return (self.__len > 0)        
    def GetSize (self) : return self.__len
    def GetAmplSize (self):
        if (self.__len > 0) : return self.__len//2 + 1
        else : return 0

    SinTbl = 0
    
    def __init__ (self, dim):
        
        if not IsValidLength (dim) : return
        
        self.__len = dim
        
        self.SinTbl = array.array ('d', (0,) * self.__len)
        
        self.__m = self.__len // 4
        
        self.SinTbl[0] = .0
        self.SinTbl[self.__m] = 1.
        self.SinTbl[2*self.__m] = .0
        self.SinTbl[-self.__m] = -1.
        
        for self.__n1 in range (1, self.__m) :
            
            self.__val_ys = math.sin (2*math.pi*self.__n1 / self.__len)
            
            self.SinTbl[self.__n1] = self.__val_ys
            self.SinTbl[self.__len//2-self.__n1] = self.__val_ys
            self.SinTbl[self.__len//2+self.__n1] = -self.__val_ys
            self.SinTbl[-self.__n1] = -self.__val_ys

        self.__memory_storage = array.array ('d', (0,) * self.__len * 4)
        self.__data_storage_offset = 0
        self.__fx_storage_offset = self.__len
        self.__free_memory_index = 2 * self.__len
        
        self.__val_sv = 0.288675134594812866     #    sqrt(3.)/6
                
    def __recursive_fast_fourier (self, data_offset, f_x_offset, n, step) :
        
        if n == 2 :
            #        FXc[0]=(x[0]+x[1])/2
            #        FXc[1]=(x[0]-x[1])/2
            self.__memory_storage[f_x_offset] = (self.__memory_storage[data_offset] + self.__memory_storage[data_offset+step]) * 0.5    
            self.__memory_storage[f_x_offset+1] = (self.__memory_storage[data_offset] - self.__memory_storage[data_offset+step]) * 0.5
               
            return
        
        f_y_offset = self.__free_memory_index
        self.__free_memory_index += n
        
        if n%3 == 0 :
            
            self.__recursive_fast_fourier (data_offset, f_y_offset, n//3, 3*step)
            self.__recursive_fast_fourier (data_offset+step, f_y_offset+n//3, n//3, 3*step)
            self.__recursive_fast_fourier (data_offset+2*step, f_y_offset+2*n//3, n//3, 3*step)
            
            self.__n1 = n // 6
            self.__m = 2 * self.__n1
            
            #    xc_1_offset -> FXc[m]            xs_1_offset -> FXs[m] 
            #    xc_2_offset -> FXc[n/3-m]        xs_2_offset -> FXs[n/3-m]
            #    xc_3_offset -> FXc[n/3+m]        xs_3_offset -> FXs[n/3+m]
            self.__xc_1_offset = f_x_offset
            self.__xc_2_offset = self.__xc_1_offset + self.__m
            self.__xc_3_offset = self.__xc_2_offset + 1
            self.__xs_1_offset = self.__xc_3_offset + self.__n1
            self.__xs_2_offset = self.__xs_1_offset + self.__m - 1
            self.__xs_3_offset = self.__xs_2_offset + 1
            
            self.__yc_offset = f_y_offset
            self.__zc_offset = self.__yc_offset + self.__m
            self.__uc_offset = self.__zc_offset + self.__m
            
            self.__val_yc = self.__memory_storage[self.__yc_offset]
            self.__yc_offset += 1; self.__ys_offset = self.__yc_offset + self.__n1  
            self.__val_zc = self.__memory_storage[self.__zc_offset]
            self.__zc_offset += 1; self.__zs_offset = self.__zc_offset + self.__n1  
            self.__val_uc = self.__memory_storage[self.__uc_offset]
            self.__uc_offset += 1; self.__us_offset = self.__uc_offset + self.__n1  
            
            #    FXc[0]      = (FYc[0] + FZc[0] + FUc[0])/3.
            #    FXc[n/3]    = FYc[0]/3. - FZc[0]/6. - FUc[0]/6.
            #    FXs[n/3]    = (FZc[0] - FUc[0]) * sqrt(3.)/6.
            self.__memory_storage[self.__xc_1_offset] = (self.__val_yc + self.__val_zc + self.__val_uc) / 3.
            self.__xc_1_offset += 1
            self.__memory_storage[self.__xc_2_offset] = self.__val_yc/3. - self.__val_zc/6. - self.__val_uc/6.
            self.__xc_2_offset -= 1
            self.__memory_storage[self.__xs_2_offset] = (self.__val_zc - self.__val_uc) * self.__val_sv
            self.__xs_2_offset -= 1
            
            # s_ij_offset -> sin (2*PI/n*(i*n/3+j*m))
            # c_ij_offset -> cos (2*PI/n*(i*n/3+j*m))
            
            self.__n1 = self.__len // 3
            self.__m = self.__len // 4
            
            self.__s_01_offset = step; self.__c_01_offset = self.__s_01_offset + self.__m 
            self.__s_11_offset = self.__s_01_offset + self.__n1; self.__c_11_offset = self.__s_11_offset + self.__m 
            self.__s_21_offset = self.__s_11_offset + self.__n1; self.__c_21_offset = self.__s_21_offset + self.__m
            if self.__c_21_offset >= self.__len : self.__c_21_offset -= self.__len
            
            self.__s_02_offset = self.__s_01_offset + step; self.__c_02_offset = self.__s_02_offset + self.__m
            self.__s_12_offset = self.__s_02_offset + self.__n1; self.__c_12_offset = self.__s_12_offset + self.__m 
            if self.__c_12_offset >= self.__len : self.__c_12_offset -= self.__len
            self.__s_22_offset = self.__s_12_offset + self.__n1; self.__c_22_offset = self.__s_22_offset + self.__m 
            if self.__s_22_offset >= self.__len : self.__s_22_offset -= self.__len
            if self.__c_22_offset >= self.__len : self.__c_22_offset -= self.__len
            
            self.__n1 = n // 6
            
            for self.__m in range (1, self.__n1) :
                
                self.__val_yc = self.__memory_storage[self.__yc_offset]; self.__yc_offset += 1 
                self.__val_ys = self.__memory_storage[self.__ys_offset]; self.__ys_offset += 1 
                self.__val_zc = self.__memory_storage[self.__zc_offset]; self.__zc_offset += 1 
                self.__val_zs = self.__memory_storage[self.__zs_offset]; self.__zs_offset += 1 
                self.__val_uc = self.__memory_storage[self.__uc_offset]; self.__uc_offset += 1 
                self.__val_us = self.__memory_storage[self.__us_offset]; self.__us_offset += 1 
            
                self.__vc_01 = self.SinTbl[self.__c_01_offset]; self.__c_01_offset += step
                if self.__c_01_offset >= self.__len : self.__c_01_offset -= self.__len
                self.__vs_01 = self.SinTbl[self.__s_01_offset]; self.__s_01_offset += step
                if self.__s_01_offset >= self.__len : self.__s_01_offset -= self.__len
            
                self.__vc_11 = self.SinTbl[self.__c_11_offset]; self.__c_11_offset += step
                if self.__c_11_offset >= self.__len : self.__c_11_offset -= self.__len
                self.__vs_11 = self.SinTbl[self.__s_11_offset]; self.__s_11_offset += step
                if self.__s_11_offset >= self.__len : self.__s_11_offset -= self.__len
            
                self.__vc_21 = self.SinTbl[self.__c_21_offset]; self.__c_21_offset += step
                if self.__c_21_offset >= self.__len : self.__c_21_offset -= self.__len
                self.__vs_21 = self.SinTbl[self.__s_21_offset]; self.__s_21_offset += step
                if self.__s_21_offset >= self.__len : self.__s_21_offset -= self.__len
            
                self.__vc_02 = self.SinTbl[self.__c_02_offset]; self.__c_02_offset += 2*step
                if self.__c_02_offset >= self.__len : self.__c_02_offset -= self.__len
                self.__vs_02 = self.SinTbl[self.__s_02_offset]; self.__s_02_offset += 2*step
                if self.__s_02_offset >= self.__len : self.__s_02_offset -= self.__len
            
                self.__vc_12 = self.SinTbl[self.__c_12_offset]; self.__c_12_offset += 2*step
                if self.__c_12_offset >= self.__len : self.__c_12_offset -= self.__len
                self.__vs_12 = self.SinTbl[self.__s_12_offset]; self.__s_12_offset += 2*step
                if self.__s_12_offset >= self.__len : self.__s_12_offset -= self.__len
            
                self.__vc_22 = self.SinTbl[self.__c_22_offset]; self.__c_22_offset += 2*step
                if self.__c_22_offset >= self.__len : self.__c_22_offset -= self.__len
                self.__vs_22 = self.SinTbl[self.__s_22_offset]; self.__s_22_offset += 2*step
                if self.__s_22_offset >= self.__len : self.__s_22_offset -= self.__len
            
                #    3*FXc[m]        = FYc[m] + FZc[m]*vc_01 - FZs[m]*vs_01 + FUc[m]*vc_02 - FUs[m]*vs_02
                #    3*FXs[m]        = FYs[m] + FZs[m]*vc_01 + FZc[m]*vs_01 + FUs[m]*vc_02 + FUc[m]*vs_02
                self.__memory_storage[self.__xc_1_offset] = (self.__val_yc + \
                    self.__val_zc*self.__vc_01 - self.__val_zs*self.__vs_01 + \
                    self.__val_uc*self.__vc_02 - self.__val_us*self.__vs_02) / 3.
                self.__xc_1_offset += 1
                self.__memory_storage[self.__xs_1_offset] = (self.__val_ys + \
                    self.__val_zs*self.__vc_01 + self.__val_zc*self.__vs_01 + \
                    self.__val_us*self.__vc_02 + self.__val_uc*self.__vs_02) / 3.
                self.__xs_1_offset += 1
            
                #    3*FXc[n/3-m]    = FYc[m] + FZc[m]*vc_21 - FZs[m]*vs_21 + FUc[m]*vc_12 - FUs[m]*vs_12
                #    3*FXs[n/3-m]    =-FYs[m] - FZs[m]*vc_21 - FZc[m]*vs_21 - FUs[m]*vc_12 - FUc[m]*vs_12
                self.__memory_storage[self.__xc_2_offset] = (self.__val_yc + \
                    self.__val_zc*self.__vc_21 - self.__val_zs*self.__vs_21 + \
                    self.__val_uc*self.__vc_12 - self.__val_us*self.__vs_12) / 3.
                self.__xc_2_offset -= 1
                self.__memory_storage[self.__xs_2_offset] = (-self.__val_ys - \
                    self.__val_zs*self.__vc_21 - self.__val_zc*self.__vs_21 - \
                    self.__val_us*self.__vc_12 - self.__val_uc*self.__vs_12) / 3.
                self.__xs_2_offset -= 1
                
                #    3*FXc[n/3+m]    = FYc[m] + FZc[m]*vc_11 - FZs[m]*vs_11 + FUc[m]*vc_22 - FUs[m]*vs_22
                #    3*FXs[n/3+m]    = FYs[m] + FZs[m]*vc_11 + FZc[m]*vs_11 + FUs[m]*vc_22 + FUc[m]*vs_22
                self.__memory_storage[self.__xc_3_offset] = (self.__val_yc + \
                    self.__val_zc*self.__vc_11 - self.__val_zs*self.__vs_11 + \
                    self.__val_uc*self.__vc_22 - self.__val_us*self.__vs_22) / 3.
                self.__xc_3_offset += 1
                self.__memory_storage[self.__xs_3_offset] = (self.__val_ys + \
                    self.__val_zs*self.__vc_11 + self.__val_zc*self.__vs_11 + \
                    self.__val_us*self.__vc_22 + self.__val_uc*self.__vs_22) / 3.
                self.__xs_3_offset += 1
            
            #    FXc[n/6] = FYc[n/6]/3. + FZc[n/6]/6. - FUc[n/6]/6.
            #    FXs[n/6] = (FZc[n/6] + FUc[n/6]) * sqrt(3.)/6.
            #    FXc[n/2] = (FYc[n/6] - FZc[n/6] + FUc[n/6])/3.
            
            self.__val_yc = self.__memory_storage[self.__yc_offset]
            self.__val_zc = self.__memory_storage[self.__zc_offset]
            self.__val_uc = self.__memory_storage[self.__uc_offset]
            
            self.__memory_storage[self.__xc_1_offset] = self.__val_yc/3. + self.__val_zc/6. - self.__val_uc/6.
            self.__memory_storage[self.__xc_3_offset] = (self.__val_yc - self.__val_zc + self.__val_uc) / 3.
            self.__memory_storage[self.__xs_1_offset] = (self.__val_zc + self.__val_uc) * self.__val_sv
            
        else : # n%2 == 0
        
            self.__recursive_fast_fourier (data_offset, f_y_offset, n//2, 2*step)
            self.__recursive_fast_fourier (data_offset+step, f_y_offset+n//2, n//2, 2*step)
        
            self.__n1 = n // 4
            self.__m = 2 * self.__n1
            
            #    xc_1_offset -> FXc[m]            xs_1_offset -> FXs[m] 
            #    xc_2_offset -> FXc[n/2-m]        xs_2_offset -> FXs[n/2-m]

            self.__xc_1_offset = f_x_offset
            self.__xc_2_offset = self.__xc_1_offset + self.__m
            
            self.__yc_offset = f_y_offset
            self.__zc_offset = self.__yc_offset + self.__m
        
            self.__val_yc = self.__memory_storage[self.__yc_offset]
            self.__yc_offset += 1; self.__ys_offset = self.__yc_offset + self.__n1  
            self.__val_zc = self.__memory_storage[self.__zc_offset]
            self.__zc_offset += 1; self.__zs_offset = self.__zc_offset + self.__n1  

            #    FXc[0] = (FYc[0] + FZc[0])/2.
            #    FXc[n/2] = (FYc[0] - FZc[0])/2.
        
            self.__memory_storage[self.__xc_1_offset] = (self.__val_yc + self.__val_zc) / 2.
            self.__xc_1_offset += 1; self.__xs_1_offset = self.__xc_1_offset + self.__m 
            self.__memory_storage[self.__xc_2_offset] = (self.__val_yc - self.__val_zc) / 2.
            self.__xc_2_offset -= 1; self.__xs_2_offset = self.__xc_2_offset + self.__m 
        
            self.__s_01_offset = step; self.__c_01_offset = self.__s_01_offset + self.__len//4
        
            for self.__m in range (1, self.__n1) :
                
                self.__val_yc = self.__memory_storage[self.__yc_offset]; self.__yc_offset += 1 
                self.__val_ys = self.__memory_storage[self.__ys_offset]; self.__ys_offset += 1 
                self.__val_zc = self.__memory_storage[self.__zc_offset]; self.__zc_offset += 1 
                self.__val_zs = self.__memory_storage[self.__zs_offset]; self.__zs_offset += 1 
                
                self.__vc_01 = self.SinTbl[self.__c_01_offset]; self.__c_01_offset += step
                if self.__c_01_offset >= self.__len : self.__c_01_offset -= self.__len
                self.__vs_01 = self.SinTbl[self.__s_01_offset]; self.__s_01_offset += step
                if self.__s_01_offset >= self.__len : self.__s_01_offset -= self.__len
        
                #    2*FXc[m]     = FYc[m] + FZc[m]*vc_01 - FZs[m]*vs_01
                #    2*FXs[m]     = FYs[m] + FZs[m]*vc_01 + FZc[m]*vs_01
                self.__memory_storage[self.__xc_1_offset] = (self.__val_yc + self.__val_zc*self.__vc_01 - self.__val_zs*self.__vs_01) * 0.5
                self.__xc_1_offset += 1
                self.__memory_storage[self.__xs_1_offset] = (self.__val_ys + self.__val_zs*self.__vc_01 + self.__val_zc*self.__vs_01) * 0.5
                self.__xs_1_offset += 1
        
                #    2*FXc[n/2-m] = FYc[m] - FZc[m]*vc_01 + FZs[m]*vs_01
                #    2*FXs[n/2-m] =-FYs[m] + FZs[m]*vc_01 + FZc[m]*vs_01
                self.__memory_storage[self.__xc_2_offset] = (self.__val_yc - self.__val_zc*self.__vc_01 + self.__val_zs*self.__vs_01) * 0.5
                self.__xc_2_offset -= 1
                self.__memory_storage[self.__xs_2_offset] = (-self.__val_ys + self.__val_zs*self.__vc_01 + self.__val_zc*self.__vs_01) * 0.5
                self.__xs_2_offset -= 1

            #    FXc[n/4] = FYc[n/4] / 2
            #    FXs[n/4] = FZc[n/4] / 2
            self.__memory_storage[self.__xc_1_offset] = self.__memory_storage[self.__yc_offset] * 0.5
            self.__memory_storage[self.__xs_1_offset] = self.__memory_storage[self.__zc_offset] * 0.5
        
        self.__free_memory_index -= n
        
        return

    #    returns success_flag, FX_coeffs
    def CalculateFourierCoefficients (self, data) :
        
        if self.__len == 0 : return False, None
        
        for self.__m in range (0, self.__len) :
            self.__memory_storage[self.__data_storage_offset+self.__m] = data[self.__m]
        
        self.__recursive_fast_fourier (self.__data_storage_offset, self.__fx_storage_offset, self.__len, 1)
                
        FX_coeffs = [0] * self.__len
        
        for self.__m in range (0, self.__len) :
            FX_coeffs[self.__m] = self.__memory_storage[self.__fx_storage_offset+self.__m]
        
        return True, FX_coeffs 
    
    #   returns success_flag, cos_coeffs, sin_coeffs
    def BuildFullCosSinCoeffs (self, FX_coeffs) :
        
        if self.__len == 0 : return False, None, None
        
        cos_coeffs = [None] * self.__len
        sin_coeffs = [0] * self.__len
        
        cos_coeffs[0] = FX_coeffs[0]
        cos_coeffs[self.__len//2] = FX_coeffs[self.__len//2]
        
        for self.__m in range (1, self.__len//2) :
            cos_coeffs[self.__m] = FX_coeffs[self.__m]
            cos_coeffs[-self.__m] = FX_coeffs[self.__m]
            sin_coeffs[self.__m] = FX_coeffs[self.__m+self.__len//2]
            sin_coeffs[-self.__m] = -FX_coeffs[self.__m+self.__len//2]

        return True, cos_coeffs, sin_coeffs  

    #   returns success_flag, data
    def ReverseFourierTransformation (self, cos_coeffs, sin_coeffs) :
        
        if self.__len == 0 : return False, None
        
        flag, F_cos = self.CalculateFourierCoefficients (cos_coeffs)
        if not flag : return False, None

        flag, F_sin = self.CalculateFourierCoefficients (sin_coeffs)
        if not flag : return False, None

        flag, Fcos_cos, Fcos_sin = self.BuildFullCosSinCoeffs (F_cos)
        if not flag : return False, None

        flag, Fsin_cos, Fsin_sin = self.BuildFullCosSinCoeffs (F_sin)
        if not flag : return False, None
        
        data = [None] * self.__len
        
        for self.__m in range (0, self.__len) :
            data[self.__m] = (Fcos_cos[self.__m] + Fsin_sin[self.__m]) * self.__len
        
        return True, data
     
    #   returns success_flag, data
    def ReverseFourierTransformation_by_coeffs (self, FX_coeffs) :
        
        if self.__len == 0 : return False

        flag, F_cos, F_sin = self.BuildFullCosSinCoeffs (FX_coeffs)
        if not flag : return False, None
        
        return self.ReverseFourierTransformation (F_cos, F_sin)

    #   returns success_flag, Ampl, Phase
    def BuildAmplitudeSpectrum (self, FX_coeffs) :
        
        if self.__len == 0 : return False, None, None
        
        ampl = [None] * (self.__len//2+1)
        phase = [None] * (self.__len//2+1)
        
        self.__val_yc = FX_coeffs[0] 
        if self.__val_yc < .0 :
            ampl[0] = -self.__val_yc
            phase[0] = math.pi
        else :
            ampl[0] = self.__val_yc
            phase[0] = .0
            
        for self.__m in range (1, self.__len//2) :
            
            self.__val_yc = FX_coeffs[self.__m]
            self.__val_ys = FX_coeffs[self.__m + self.__len//2]
            
            self.__val_zc = self.__val_yc*self.__val_yc + self.__val_ys*self.__val_ys
            
            if self.__val_zc > 0 :
                ampl[self.__m] = math.sqrt (2.*self.__val_zc)
                phase[self.__m] = math.atan2 (self.__val_ys, self.__val_yc)
            else :
                ampl[self.__m] = 0
                phase[self.__m] = 0

        self.__val_yc = FX_coeffs[self.__len//2] 
        if self.__val_yc < .0 :
            ampl[self.__len//2] = -self.__val_yc
            phase[self.__len//2] = math.pi
        else : 
            ampl[self.__len//2] = self.__val_yc
            phase[self.__len//2] = .0
            
        return True, ampl, phase

    #   returns success_flag, F_XY_coeffs
    def BuildCrossFourierCoefficients (self, FX_coeffs, FY_coeffs) :
        
        if self.__len == 0 : return False, None
        
        F_XY_coeffs = [None] * self.__len
        
        F_XY_coeffs[0] = FX_coeffs[0] * FY_coeffs[0]

        for self.__m in range (1, self.__len//2) :
            
            self.__val_zc = FX_coeffs[self.__m]
            self.__val_zs = FX_coeffs[self.__m + self.__len//2]
            self.__val_yc = FY_coeffs[self.__m]
            self.__val_ys = FY_coeffs[self.__m + self.__len//2]
            
            F_XY_coeffs[self.__m] = self.__val_zc*self.__val_yc + self.__val_zs*self.__val_ys
            F_XY_coeffs[self.__m+self.__len//2] = self.__val_zc*self.__val_ys - self.__val_zs*self.__val_yc
            
        F_XY_coeffs[self.__len//2] = FX_coeffs[self.__len//2] * FY_coeffs[self.__len//2]

        return True, F_XY_coeffs
    