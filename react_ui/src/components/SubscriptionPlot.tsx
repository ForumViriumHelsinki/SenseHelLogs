import React from 'react';
import {AttributeSubscription, Subscription} from "components/types";
// @ts-ignore
import Plot from 'react-plotly.js';
import sessionRequest from "sessionRequest";
import {subscriptionUrl} from "urls";
import {Alert, Button, Spinner} from "reactstrap";

type SubscriptionReportProps = {
  subscriptionUUID: string,
  from?: any, // Timestamp in some form
  displayModeBar?: boolean,
  title?: string,
  provideCSV?: boolean,
  height?: number
}

export default class SubscriptionPlot extends React.Component<SubscriptionReportProps> {
  colors = ['#FF5000', '#009E92', '#d70074', '#28a745', '#6610f2']

  state:
    {subscription: Subscription | null, error: boolean, loading: boolean}
    =
    {subscription: null, error: false, loading: true};

  componentDidMount() {
    const {subscriptionUUID, from} = this.props;
    if (subscriptionUUID) this.fetchSubscription();
    else this.setState({error: true, loading: false});
  }

  componentDidUpdate(prevProps: Readonly<SubscriptionReportProps>, prevState: Readonly<{}>, snapshot?: any): void {
    if (prevProps != this.props) this.fetchSubscription();
  }

  private fetchSubscription() {
    const {subscriptionUUID, from} = this.props;
    this.setState({error: false, loading: true});
    sessionRequest(subscriptionUrl(subscriptionUUID as string, from)).then(response => {
      if (response.status >= 400) this.setState({error: true, loading: false});
      else response.json().then(subscription => this.setState({subscription, loading: false}));
    });
  }

  render() {
    const {loading, error, subscription} = this.state;
    const {subscriptionUUID, displayModeBar, provideCSV, from} = this.props;

    return (
      loading ?
        <div className="text-center mt-4"><Spinner/></div>
      : error ?
        <Alert color="danger">
          {subscriptionUUID ? `Failed to load subscription with id ${subscriptionUUID}.` : 'No subscription id given.'}
        </Alert>
      :
        <>
          <Plot data={this.getPlotData()}
                layout={this.getLayout()}
                config={{displayModeBar: displayModeBar || false}} />
          {provideCSV && subscription &&
            <div className="m-1">
              Download csv:<br/>
              {subscription.attributes.map((attribute) =>
                <a className="btn btn-sm btn-outline-primary m-1"
                   key={attribute.description}
                   href={this.csvURI(attribute)}
                   download={`${attribute.description}_${from || 'all'}.csv`}>
                  {attribute.description}
                </a>
              )}
            </div>
          }
        </>
    )
  }

  private getLayout() {
    const {title, displayModeBar, height} = this.props;
    const attributes = (this.state.subscription as Subscription).attributes;
    const px = 1 / window.innerWidth;
    const yaxisWidth = 24*px;

    return {
      width: window.innerWidth,
      height: height || Math.min(window.innerHeight, window.innerWidth),
      margin: {l: 0, r: 8, t: (title || displayModeBar) ? 32 : 10},
      title: title || '',
      xaxis: {domain: [4 * px + yaxisWidth * attributes.length, 1]},
      legend: {orientation: 'h', bgcolor: 'transparent'},
      ...Object.fromEntries(attributes.map(({description}, i) =>
        [`yaxis${i ? i + 1 : ''}`, {
          title: '',
          color: this.colors[i],
          anchor: i ? 'free' : undefined,
          overlaying: i ? 'y': undefined,
          side: 'left',
          position: yaxisWidth * (i + 1),
          tickfont: {size: 10}
        }]
      ))};
  }

  getPlotData() {
    const subscription = this.state.subscription as Subscription;
    return subscription.attributes.map(({description, values}, i) => ({
      x: values.map(({timestamp}) => timestamp),
      y: values.map(({value}) => value),
      type: 'scatter',
      mode: 'lines',
      name: description,
      yaxis: i ? `y${i+1}` : undefined,
      line: {color: this.colors[i], width: 1},
      opacity: 0.6
    }))
  }

  private csvURI(attribute: AttributeSubscription) {
    return encodeURI(
      "data:text/csv;charset=utf-8,timestamp,value\n" +
      attribute.values.map(({timestamp, value}) => [timestamp, value].join(',')).join('\n'));
  }
}
