import {render, screen} from 'sentry-test/reactTestingLibrary';

import {MessageSpanSamplesTable} from 'sentry/views/performance/queues/destinationSummary/messageSpanSamplesTable';
import {MessageActorType} from 'sentry/views/performance/queues/settings';

describe('messageSpanSamplesTable', () => {
  it('renders consumer samples table', () => {
    render(
      <MessageSpanSamplesTable
        data={[]}
        isLoading={false}
        type={MessageActorType.CONSUMER}
      />
    );
    expect(screen.getByRole('table', {name: 'Span Samples'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Span ID'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Message ID'})).toBeInTheDocument();
    expect(
      screen.getByRole('columnheader', {name: 'Processing Time'})
    ).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Retries'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Status'})).toBeInTheDocument();
  });
  it('renders producer samples table', () => {
    render(
      <MessageSpanSamplesTable
        data={[]}
        isLoading={false}
        type={MessageActorType.PRODUCER}
      />
    );
    expect(screen.getByRole('table', {name: 'Span Samples'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Span ID'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Message ID'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Message Size'})).toBeInTheDocument();
    expect(screen.getByRole('columnheader', {name: 'Status'})).toBeInTheDocument();
  });
});
