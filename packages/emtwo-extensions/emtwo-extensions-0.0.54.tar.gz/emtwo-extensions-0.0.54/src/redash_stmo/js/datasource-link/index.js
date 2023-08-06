import debug from 'debug';
import template from './datasource-link.html';

const logger = debug('redash:datasourceLink');

function controller($rootScope, $location, $uibModal, Auth, currentUser, clientConfig, Dashboard) {
  this.basePath = clientConfig.basePath;
  this.currentUser = currentUser;
}

export default function init(ngModule) {
  ngModule.component('datasourceLink', {
    template,
    controller,
  });
}
