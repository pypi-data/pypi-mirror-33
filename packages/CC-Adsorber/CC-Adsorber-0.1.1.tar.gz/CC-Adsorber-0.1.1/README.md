# Adsorber
Install instructions
```
cd /path/to/Adsorber
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt

For PyQt4 (SiteFilterGui)
cd /path/to/Adsorber/.env/bin/
wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.8/sip-4.19.8.tar.gz
tar -xzf sip-4.19.8.tar.gz
cd sip-4.19.8
python config.py
make install

cd /path/to/Adsorber/.env/bin/
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12.1/PyQt4_gpl_x11-4.12.1.tar.gz
tar -xzf PyQt4_gpl_x11-4.12.1.tar.gz
cd PyQt4_gpl_x11-4.12.1
python config.py
make install
(ignore errors)
```
