<p align="center">
  <img src="luluflix.png" height="52" alt="Luluflix" />
</p>

<h1 align="center">outils vidéo</h1>

<p align="center">
  Outil interne pour incruster le logo du Progrès sur vos vidéos et photos,<br/>
  extraire une capture d'écran ou couper un segment vidéo.<br/>
  <strong>Aucune donnée n'est conservée sur un serveur.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
</p>

---

## Fonctionnalités

| Onglet | Description |
|--------|-------------|
| **Watermark vidéo** | Incrustation du logo du Progrès en coin haut-droit, export MP4 H.264 |
| **Watermark photo** | Incrustation du logo sur PNG / JPG, export sans perte de qualité |
| **Capture d'écran** | Saisie manuelle du timecode pour extraire une frame précise, export PNG |
| **Couper une vidéo** | Lecteur vidéo intégré avec timeline de sélection, coupe sans réencodage |

---

## Lancer en local

**Prérequis** : Python 3.10+, FFmpeg installé sur le système.

```bash
git clone https://github.com/lucasbe-lpr/app-watermark.git
cd app-watermark
pip install -r requirements.txt
streamlit run app.py
```

L'app s'ouvre sur [http://localhost:8501](http://localhost:8501).

---

## Déploiement sur Streamlit Cloud

1. Pusher ce dépôt sur votre compte GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Sélectionner le dépôt, la branche `main` et le fichier `app.py`
4. Cliquer sur **Deploy** — FFmpeg est installé automatiquement via `packages.txt`

---

## Structure du projet

```
app-watermark/
├── app.py              # Application principale (4 onglets)
├── requirements.txt    # Dépendances Python (streamlit, pillow)
├── packages.txt        # Dépendances système (ffmpeg)
```

---

## Stack technique

- **[Streamlit](https://streamlit.io)** — interface web Python
- **[FFmpeg](https://ffmpeg.org)** — encodage vidéo, coupe `-c copy`, extraction de frames
- **[Pillow](https://pillow.readthedocs.io)** — composition du logo sur les images
- **HTML/JS custom** — lecteur vidéo, sliders et timelines via `st.components.v1.html`

---

## Notes techniques

**Logo** : taille calculée sur la diagonale du média (`√(W²+H²) × 0.1307`), garantissant un ratio visuel constant quelle que soit l'orientation. Positionné à 5 % depuis le bord droit et 7 % depuis le haut.

**Coupe sans réencodage** : `ffmpeg -ss -to -c copy` est instantané quelle que soit la durée.

**Capture** : `ffmpeg -ss {timecode} -vframes 1` — précision à la frame près.

**Taille max recommandée** : les vidéos sont encodées en base64 pour le lecteur HTML intégré. Au-delà de ~150 Mo le navigateur peut ralentir sur l'onglet Couper.

---

<p align="center">© luluflix</p>
