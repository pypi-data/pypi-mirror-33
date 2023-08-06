Version 0.0.1
This is a project to create the software infrastructure to:

1. Automate the job submission process of DFT calculations for catalyst screening

2. Log DFT calculation results in a shared database for public use

3. Develop database architectures, analytical tools, and data visualizations
initialize your system with the following commands:
```
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt

For PyQt4 (SiteFilterGui)
cd path/to/CataLog/.env/bin/
wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.8/sip-4.19.8.tar.gz
tar -xzf sip-4.19.8.tar.gz
cd sip-4.19.8
python config.py
make install

cd path/to/CataLog/.env/bin/
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12.1/PyQt4_gpl_x11-4.12.1.tar.gz
tar -xzf PyQt4_gpl_x11-4.12.1.tar.gz
cd PyQt4_gpl_x11-4.12.1
python configure-ng.py
make install
(ignore errors)
```

and make sure the following environment variables are declared
