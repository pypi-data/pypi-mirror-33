import { find } from 'underscore';
import debug from 'debug';
import template from './datasource-link.html';

const logger = debug('redash:datasourceLink');

function controller($scope, $route, $routeParams, $http, $location) {
  let dataSources = $route.current.locals.dataSources;
  let query = $route.current.locals.query
  $scope.dataSource = find(dataSources, ds => ds.id === query.data_source_id);
}

export default function init(ngModule) {
  ngModule.component('datasourceLink', {
    template,
    controller,
  });
}
