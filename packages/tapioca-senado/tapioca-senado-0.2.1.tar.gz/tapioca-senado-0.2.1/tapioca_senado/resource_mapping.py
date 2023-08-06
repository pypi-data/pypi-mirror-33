# coding: utf-8

RESOURCE_MAPPING = {

    # Senadores
    'senadores': {
        'resource': 'senador/lista/atual',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaSenadorService/resource_ListaSenadorService_listaSenadoresXml_GET',
    },

    # Comissões
    'comissoes': {
        'resource': 'comissao/lista/colegiados',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaComissaoService/resource_ListaComissaoService_listaColegiadosXml_GET',
    },
    'comissoes_por_tipo': {
        'resource': 'comissao/lista/{tipo}',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/resource_ListaComissaoService.html',
    },
}
