import {OrganizationFixture} from 'sentry-fixture/organization';

import {render, screen} from 'sentry-test/reactTestingLibrary';

import {useLocation} from 'sentry/utils/useLocation';
import usePageFilters from 'sentry/utils/usePageFilters';
import WebVitalsLandingPage from 'sentry/views/performance/browser/webVitals/webVitalsLandingPage';

jest.mock('sentry/utils/useLocation');
jest.mock('sentry/utils/usePageFilters');

describe('WebVitalsLandingPage', function () {
  const organization = OrganizationFixture({
    features: ['insights-initial-modules'],
  });

  beforeEach(function () {
    jest.mocked(useLocation).mockReturnValue({
      pathname: '',
      search: '',
      query: {},
      hash: '',
      state: undefined,
      action: 'PUSH',
      key: '',
    });
    jest.mocked(usePageFilters).mockReturnValue({
      isReady: true,
      desyncedFilters: new Set(),
      pinnedFilters: new Set(),
      shouldPersist: true,
      selection: {
        datetime: {
          period: '10d',
          start: null,
          end: null,
          utc: false,
        },
        environments: [],
        projects: [],
      },
    });

    MockApiClient.addMockResponse({
      url: `/organizations/${organization.slug}/events/`,
      body: {
        data: [],
      },
    });
    MockApiClient.addMockResponse({
      url: `/organizations/${organization.slug}/events-stats/`,
      body: {},
    });
  });

  afterEach(function () {
    jest.resetAllMocks();
  });

  it('renders FID deprecation alert', async () => {
    jest.mocked(useLocation).mockReturnValue({
      pathname: '',
      search: '',
      query: {useStoredScores: 'true'},
      hash: '',
      state: undefined,
      action: 'PUSH',
      key: '',
    });
    render(<WebVitalsLandingPage />, {organization});
    await screen.findByText(/\(Interaction to Next Paint\) will replace/);
    await screen.findByText(
      /\(First Input Delay\) in our performance score calculation./
    );
  });
});
