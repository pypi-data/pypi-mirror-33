# -*- coding:utf-8 -*-
from interlegis.portalmodelo.policy.config import PROJECTNAME
from plone.app.upgrade.utils import loadMigrationProfile
from plone import api

import logging

PROFILE_ID = 'interlegis.portalmodelo.policy:default'
PRODUCTS = ('interlegis.portalmodelo.theme')

def apply_configurations(context):
    """Atualiza perfil para versao 4."""
    logger = logging.getLogger(PROJECTNAME)
    profile = 'profile-interlegis.portalmodelo.policy.upgrades.v4:default'
    loadMigrationProfile(context, profile)
    logger.info('Atualizado para versao 4')

    q_i = api.portal.get_tool(name='portal_quickinstaller')

    for up in PRODUCTS:
        if q_i.isProductInstalled(up):
            q_i.uninstallProducts([up])
    logger.info('Desinstalando produto de tema para adicionar views para áudio e vídeo ao vivo.')

    if not q_i.isProductInstalled('interlegis.portalmodelo.theme'):
        q_i.installProduct('interlegis.portalmodelo.theme')
    logger.info('Instalado produto de tema para adicionar views para áudio e vídeo ao vivo.')

