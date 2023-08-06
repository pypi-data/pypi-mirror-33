#! python
# -*- coding: utf-8 -*-

"""Magnetic resonance experiment simulator and visualization tool.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>

Since:
    2015/07/01

"""

__all__ = ['system', 'simulator', 'sequence', 'subject', 'gui']
__version__ = '1.2.1'

package = 'mrsprint'
project = "MR SPRINT"
project_no_spaces = project.replace(' ', '')
description = 'Magnetic resonance experiment simulator and visualization tool.'

authors = ['Daniel Cosmo Pizetta', 'Victor Hugo de Mello Pessoa']
authors_string = ', '.join(authors)
emails = ['daniel.pizetta@usp.br', 'victor.pessoa@usp.br']
emails_string = ', '.join(emails)

org_name = 'Sao Carlos Institute of Physics - University of Sao Paulo'
org_domain = 'www.ifsc.usp.br'

license = 'MIT, CC-BY'
copyright = '2015-2018 ' + authors_string

url = 'https://gitlab.com/dpizetta/mrsprint'
pypi_url = 'https://pypi.org/project/mrsprint/'
rtd_url = 'https://mrsprint.readthedocs.io/en/latest/'
