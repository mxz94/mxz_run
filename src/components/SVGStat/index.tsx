import { lazy, Suspense } from 'react';
import { totalStat } from '@assets/index';
import { loadSvgComponent } from '@/utils/svgUtils';
import useActivities from '@/hooks/useActivities';
import RunRow from '../RunTable/RunRow';
import styles from './style.module.css';

// Lazy load both github.svg and grid.svg
const GithubSvg = lazy(() => loadSvgComponent(totalStat, './github.svg'));

const GridSvg = lazy(() => loadSvgComponent(totalStat, './grid.svg'));
const { activities } = useActivities();

let runs = activities;

const SVGStat = () => (
  <div id="svgStat">
    <Suspense fallback={<div className="text-center">Loading...</div>}>
    <div className={styles.tableContainer}>
      <table className={styles.runTable} cellSpacing="0" cellPadding="0">
        <thead>
          <tr>
          <th />
              <th key="类型">
                类型
              </th>
              <th key="距离">
              距离
              </th>
              <th key="配速">
              配速
              </th>
              <th key="时速">
              时速
              </th>
              <th key="时长">
              时长
              </th>
              <th key="日期">
              日期
              </th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <RunRow
              key={run.run_id}
              run={run}
              runIndex={0}
            />
          ))}
        </tbody>
      </table>
    </div>
      <GithubSvg className="mt-4 h-auto w-full" />
      <GridSvg className="mt-4 h-auto w-full" />
    </Suspense>
  </div>
);

export default SVGStat;
