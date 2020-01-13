import React from "react";
import SubscriptionPlot from "components/SubscriptionPlot";
import {Nav, NavItem, NavLink} from "reactstrap";
import moment from "moment";

class NavBar extends React.Component {
  render() {
    return <nav className="navbar navbar-dark bg-primary mb-2">
      <div className="w-25"></div>
      <h5 className="mt-1 text-light">Data Wallet</h5>
      <div className="w-25 d-flex justify-content-end">
        <img style={{maxHeight: 48, marginRight: -16}} src="images/FORUM_VIRIUM_logo_white.png"/>
      </div>
    </nav>;
  }
}

const intervalOptions = [
  ['One day', moment().subtract(1, 'day')],
  ['One week', moment().subtract(1, 'week')],
  ['One month', moment().subtract(1, 'month')],
  ['All', null]
];

export class SubscriptionReport extends React.Component<{ subscriptionUUID: string }> {
  state: { valuesFrom: any } = {valuesFrom: intervalOptions[1][1]};

  render() {
    const {valuesFrom} = this.state;

    return <>
      <NavBar/>
      <div className="mt-1 mr-1 mb-4 ml-1">
        <Nav pills>
          {intervalOptions.map(([label, timestamp]) =>
            <NavItem key={label as string}>
              <NavLink active={valuesFrom == timestamp} onClick={() => this.setState({valuesFrom: timestamp})}>
                {label}
              </NavLink>
            </NavItem>
          )}
        </Nav>
      </div>
      <SubscriptionPlot subscriptionUUID={this.props.subscriptionUUID}
                        provideCSV={true}
                        displayModeBar={true} from={valuesFrom ? valuesFrom.toISOString() : undefined}
                        height={window.innerHeight - 260}/>
    </>
  }
}