import React from 'react';
import {BrowserRouter as Router, Route, Switch} from "react-router-dom";

import SubscriptionPlot from "components/SubscriptionPlot";
import moment from "moment";
import {SubscriptionReport} from "components/SubscriptionReport";

type RouterProps = {}

export default class AppRouter extends React.Component<RouterProps> {
  private getSubscriptionUUID() {
    return new URLSearchParams(window.location.search).get('subscription');
  }

  render() {
    const subscriptionUUID = this.getSubscriptionUUID() as string;
    const oneDay = moment().subtract(1, 'days').toISOString();
    return (
      <Router>
        <Switch>
          <Route path='/preview/'>
            <SubscriptionPlot subscriptionUUID={subscriptionUUID} from={oneDay}/>
          </Route>
          <Route path='/'>
            <SubscriptionReport subscriptionUUID={subscriptionUUID}/>
          </Route>
        </Switch>
      </Router>
    );
  }
}
