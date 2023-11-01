from flask import Flask, render_template, Response, request
from DetecteurVideo import DetecteurVideo
import numpy as np
import CalculateurFFT

app = Flask(__name__)

@app.route('/')
def index():  
    return render_template("index.html")

@app.route("/envoyer_rectangle_max", methods = ["POST"])
def rectangle_max():
    jsn = request.get_json(force=True)
    detecteurVideo.rectangle_max = jsn["rectangle_limite"]
    return ""

@app.route("/envoyer_rectangle_min", methods = ["POST"])
def rectangle_min():
    jsn = request.get_json(force=True)
    detecteurVideo.rectangle_min = jsn["rectangle_limite"]
    return ""

@app.route("/recuperer_positions_radars", methods=["POST"])
def recuperer_positions_radars():
    jsn = request.get_json(force=True)
    positions_radars = {} 
    for nom_radar in ["Ard", "RPi_1", "RPi_2"]:
        if "vecteur_unitaire" in jsn[nom_radar] and "point_radar" in jsn[nom_radar]:
            positions_radars[nom_radar] = {
                "vecteur_unitaire" : jsn[nom_radar]["vecteur_unitaire"],
                "point_radar" : jsn[nom_radar]["point_radar"]
            }
    detecteurVideo.positions_radars = positions_radars
    return ""

@app.route("/recuperer_mesures", methods=["GET"])
def recuperer_mesures():
    dsp = {}
    N = 8       #On affiche 1/4
    N_min = (int(N/2) - 1)/N
    N_max = (int(N/2) + 1)/N
    for radar in ["Ard", "RPi_1", "RPi_2"] :
        I = 2000*np.sin(2*np.pi*(24.005e9)*np.array([t for t in range(750)])) + np.random.normal(1, 1, 750)
        Q = 2000*np.sin(2*np.pi*(24.005e9)*np.array([t for t in range(750)])) + np.random.normal(1, 1, 750)
        dsp_radar = CalculateurFFT.calculerFFT({"I" : I, "Q" : Q}, 1024, 30, 25, 0.05)
        dsp_radar_FFT = dsp_radar["FFT"]    

        dsp_radar["associations"] = CalculateurFFT.associations_frequences(dsp_radar_FFT)

        dsp_radar_FFT = dsp_radar["FFT"]
        frequences = dsp_radar_FFT["frequences"]
        dsp_radar_FFT["frequences"] = frequences[int(N_min*len(frequences)):int(N_max*len(frequences))]
        for fft in [dsp_radar_FFT["fft_m1"], dsp_radar_FFT["fft_d1"], dsp_radar_FFT["fft_m2"], dsp_radar_FFT["fft_d2"]]:
            fft["seuils"] = fft["seuils"] [int(N_min*len(fft["seuils"] )):int(N_max*len(fft["seuils"]))]
            fft["fft"] = fft["fft"] [int(N_min*len(fft["fft"])):int(N_max*len(fft["fft"]))]
        
        dsp[radar] = dsp_radar
        
    return dsp

@app.route("/flux_video")
def flux_video():
    detecteurVideo.positions_radars = {} 
    return Response(detecteurVideo.lancer_detection(), 
        mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__=="__main__": 
    detecteurVideo = DetecteurVideo()
    app.run(debug=True)
    



