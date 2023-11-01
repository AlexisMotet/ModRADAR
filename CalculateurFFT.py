import numpy as np
from scipy.ndimage import convolve
from scipy.signal import find_peaks

def CA_CFARv2(fft, frequences, n_train, n_guard, fa_rate=1/1000):
    alpha = n_train * (fa_rate ** (-1 / n_train) - 1)
    ones = np.ones(n_train//2)
    zeros = np.zeros(n_guard)
    kernel = np.concatenate([ones, zeros, ones])
    conv = convolve(fft, kernel, mode="constant")
    mean = conv/n_train
    thresholds = mean*alpha
    peaks, properties = find_peaks(fft, height=thresholds, distance=(n_train + n_guard)//2)
    return peaks.tolist(), [frequences[i] for i in peaks], \
        properties["peak_heights"].tolist(), thresholds.tolist()
                
def calculerFFT(echantillons, N_FFT, n_train, n_guard, taux_fa):
    Ns =  200
    Fs =  200000
    frequences =  [-Fs/2 + ((Fs*i)/N_FFT) for i in range(N_FFT)]
    max_voltage = 3.3
    ADC_bits = 12
    ADC_intervals = 2 ** ADC_bits

    I, Q = echantillons["I"], echantillons["Q"]
    I, Q = np.array(echantillons["I"]), np.array(echantillons["Q"])

    I = I*(max_voltage/ADC_intervals) - np.mean(I*(max_voltage / ADC_intervals))
    Q = Q*(max_voltage/ADC_intervals) - np.mean(Q*(max_voltage / ADC_intervals))

    I_m1 = I[0:Ns]
    Q_m1 = Q[0:Ns]
    I_d1 = I[Ns:2*Ns]
    Q_d1 = Q[Ns:2*Ns]

    I_m2 = I[2*Ns:int(2.75*Ns)]
    Q_m2 = Q[2*Ns:int(2.75*Ns)]
    I_d2 = I[int(2.75*Ns):int(3.5*Ns)]
    Q_d2 = Q[int(2.75*Ns):int(3.5*Ns)]

    vecteur_complexe_m1 = I_m1 + 1j*Q_m1
    vecteur_complexe_d1 = I_d1 - 1j*Q_d1

    vecteur_complexe_m2 = I_m2 + 1j*Q_m2
    vecteur_complexe_d2 = I_d2 - 1j*Q_d2

    vecteur_complexe_m1 = vecteur_complexe_m1*np.hanning(Ns)*2/3.3
    vecteur_complexe_d1 = vecteur_complexe_d1*np.hanning(Ns)*2/3.3

    vecteur_complexe_m2 = vecteur_complexe_m2*np.hanning(0.75*Ns)*2/3.3
    vecteur_complexe_d2 = vecteur_complexe_d2*np.hanning(0.75*Ns)*2/3.3

    fft_m1 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_m1/Ns, N_FFT)))
    fft_d1 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_d1/Ns, N_FFT)))

    fft_m2 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_m2/(0.75*Ns), N_FFT)))
    fft_d2 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_d2/(0.75*Ns), N_FFT)))

    FFT_m1 = {"fft" : fft_m1}
    FFT_d1 = {"fft" : fft_d1}

    FFT_m2 = {"fft" : fft_m2}
    FFT_d2 = {"fft" : fft_d2}

    FFT_m1["indices_pics"], FFT_m1["frequences_pics"], FFT_m1["valeurs_pics"], FFT_m1["seuils"] \
            = CA_CFARv2(fft_m1, frequences, n_train, n_guard, taux_fa)  
            
    FFT_d1["indices_pics"], FFT_d1["frequences_pics"], FFT_d1["valeurs_pics"], FFT_d1["seuils"] \
            = CA_CFARv2(fft_d1, frequences, n_train, n_guard, taux_fa)  


    FFT_m2["indices_pics"], FFT_m2["frequences_pics"], FFT_m2["valeurs_pics"], FFT_m2["seuils"] \
            = CA_CFARv2(fft_m2, frequences, n_train, n_guard, taux_fa)     

    FFT_d2["indices_pics"], FFT_d2["frequences_pics"], FFT_d2["valeurs_pics"], FFT_d2["seuils"] \
            = CA_CFARv2(fft_d2, frequences, n_train, n_guard, taux_fa) 

    FFT_m1["fft"] = FFT_m1["fft"].tolist()
    FFT_d1["fft"] = FFT_d1["fft"].tolist()

    FFT_m2["fft"] = FFT_m2["fft"].tolist()
    FFT_d2["fft"] = FFT_d2["fft"].tolist() 

    return {"FFT" : {
                "fft_m1" : FFT_m1,
                "fft_d1" : FFT_d1,
                "fft_m2" : FFT_m2,
                "fft_d2" :  FFT_d2,
                "frequences" : frequences,
                },
            }

def associations_frequences(dsp, f0=5, BW=240, e=1):
    Ns = 200
    c = 3e8
    f0 = (24000 + f0)*1e6
    BW = BW * 1e6
    Fs  = 200000
    points_potentiels = []
    points_certains = []
    
    droites_m1, droites_d1 = [], []
    for f_m1 in dsp["fft_m1"]["frequences_pics"] :
        droite = {
            "m" : -(f0*(Ns/Fs))/BW,
            "b" : (f_m1*c*(Ns/Fs))/(2*BW)
        }
        droites_m1.append(droite)
    for f_d1 in dsp["fft_d1"]["frequences_pics"] :
        droite = {
            "m" : (f0*(Ns/Fs))/BW,
            "b" : (f_d1 *c*(Ns/Fs))/(2*BW)
        }
        droites_d1.append(droite)

    droites_m2, droites_d2 = [], []
    for f_m2 in dsp["fft_m2"]["frequences_pics"] :
        droite = {
            "m" : -(f0*(0.75*(Ns/Fs)))/BW,
            "b" : (f_m2 *c*(0.75*(Ns/Fs)))/(2*BW)
        }
        droites_m2.append(droite)
    for f_d2 in dsp["fft_d2"]["frequences_pics"] :
        droite = {
            "m" : (f0*(0.75*(Ns/Fs)))/BW,
            "b" : (f_d2*c*(0.75*(Ns/Fs)))/(2*BW)
        }
        droites_d2.append(droite)

    droites_utilisees = []
    for d_m1 in droites_m1:
        for d_d1 in droites_d1:
            if not d_d1 in droites_utilisees :
                v = (d_m1["b"]-d_d1["b"])/(d_d1["m"] - d_m1["m"])
                d =  d_d1["m"]*v + d_d1["b"] 
                intersection = {
                    "v" : v,
                    "d" : d
                }
                for d_m2 in droites_m2 :
                    if not d_m2 in droites_utilisees :
                        if abs(d_m2["m"]*intersection["v"]+d_m2["b"]
                                - intersection["d"])<e :
                            points_potentiels.append(intersection)
                            droites_utilisees+= [d_m1, d_d1, d_m2]
                            for d_d2 in droites_d2:
                                if not d_d2 in droites_utilisees :
                                    if abs(d_d2["m"]*intersection["v"]+d_d2["b"]
                                            - intersection["d"])<e :
                                        points_certains.append(intersection)
                                        droites_utilisees.append(d_d2)           
    return {
        "points" : {
            "points_certains" : points_certains, 
            "points_potentiels" : points_potentiels
        },
        "droites" : {
            "droites_d1" : droites_d1,
            "droites_m1" : droites_m1, 
            "droites_m2" : droites_m2,
            "droites_d2" : droites_d2,
        }
    }