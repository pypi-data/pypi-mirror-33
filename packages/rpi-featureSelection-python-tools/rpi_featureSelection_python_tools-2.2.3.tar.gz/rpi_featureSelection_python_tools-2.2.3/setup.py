from setuptools import setup

setup(
	name='rpi_featureSelection_python_tools',  # This is the name of your PyPI-package. 
	version= '2.2.3',  # Update the version number for new releases
	author='Keyi Liu, Zijun Cui, Qiang Ji',
	author_email='cuiz3@rpi.edu',
	url='https://www.ecse.rpi.edu/~cvrl/',
	description='RPI primitives using the latest 2018.6.20 APIs second submission',
	platforms=['Linux', 'MacOS'],
        keywords = 'd3m_primitive',
	entry_points = {
		'd3m.primitives': [
			'rpi_featureSelection_python_tools.IPCMBplus_Selector = rpi_featureSelection_python_tools.feature_selector:IPCMBplus_Selector',
			'rpi_featureSelection_python_tools.JMIplus_Selector = rpi_featureSelection_python_tools.feature_selector:JMIplus_Selector',
			'rpi_featureSelection_python_tools.STMBplus_Selector = rpi_featureSelection_python_tools.feature_selector:STMBplus_Selector',
			'rpi_featureSelection_python_tools.aSTMBplus_Selector = rpi_featureSelection_python_tools.feature_selector:aSTMBplus_Selector',
			'rpi_featureSelection_python_tools.sSTMBplus_Selector = rpi_featureSelection_python_tools.feature_selector:sSTMBplus_Selector',
			'rpi_featureSelection_python_tools.F_STMB_Selector = rpi_featureSelection_python_tools.feature_selector:F_STMB_Selector',
			'rpi_featureSelection_python_tools.F_aSTMB_Selector = rpi_featureSelection_python_tools.feature_selector:F_aSTMB_Selector',
			'rpi_featureSelection_python_tools.F_sSTMB_Selector = rpi_featureSelection_python_tools.feature_selector:F_sSTMB_Selector',
                        'rpi_featureSelection_python_tools = workaround_ignore_error'	
		],
	},
	packages=['rpi_featureSelection_python_tools']
)
