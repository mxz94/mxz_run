import { lazy, Suspense } from 'react';
import { totalStat } from '@assets/index';
import { loadSvgComponent } from '@/utils/svgUtils';
import useActivities from '@/hooks/useActivities';
import RunRow from '../RunTable/RunRow';
import styles from './style.module.css';
import { Activity, RunIds } from '@/utils/utils';

interface IRunTableProperties {
  locateActivity: (_runIds: RunIds) => void;
  setActivity: (_runs: Activity[]) => void;
  runIndex: number;
  setRunIndex: (_index: number) => void;
}


// Lazy load both github.svg and grid.svg
const GithubSvg = lazy(() => loadSvgComponent(totalStat, './github.svg'));

const GridSvg = lazy(() => loadSvgComponent(totalStat, './grid.svg'));
const { activities } = useActivities();

let runs = activities;
let run_speed =  0
let max_run;
let run_10_speed =  0
let max_run_10;
let run_bm_speed =  0
let max_run_bm;
let run_qm_speed =  0
let max_run_qm;
let ride_speed =  0
let max_ride;
runs.forEach(item => {
    if (item.type == "Run") {
      if (item.average_speed > run_speed && item.distance >= 5000  &&  item.distance < 5500) {
        run_speed = item.average_speed
        max_run = item
        max_run.name = "5km跑"
      }
      if (item.average_speed > run_10_speed && item.distance >= 10000  &&  item.distance < 10500) {
        run_10_speed = item.average_speed
        max_run_10 = item
        max_run_10.name = "10km跑"
      }
      if (item.average_speed > run_bm_speed && item.distance >= 21097.5  &&  item.distance < 21597.5) {
        run_bm_speed = item.average_speed
        max_run_bm = item
        max_run_bm.name = "半马跑"
      }
      if (item.average_speed > run_qm_speed && item.distance > 42195  &&  item.distance < 42695) {
        run_qm_speed = item.average_speed
        max_run_qm = item
        max_run_qm.name = "全马跑"
      }
    } 
    if (item.type == "Ride") {
      if (item.average_speed > ride_speed) {
        ride_speed = item.average_speed
        max_ride = item
      }
    }
})
let new_runs:any[] = []
if (max_run) new_runs.push(max_run)
if (max_run_10) new_runs.push(max_run_10)
if (max_run_bm) new_runs.push(max_run_bm)
if (max_run_qm) new_runs.push(max_run_qm)
if (max_ride) new_runs.push(max_ride)


const SVGStat = ({locateActivity,
  setActivity,
  runIndex,
  setRunIndex,
}: IRunTableProperties) => (
  <div id="svgStat">
    <Suspense fallback={<div className="text-center">Loading...</div>}>
    <div className={styles.tableContainer}>
      <table className={styles.runTable} cellSpacing="0" cellPadding="0">
        <thead>
          <tr>
          <th key="历史最佳">
          历史最佳
          </th>
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
          {new_runs.map((run) => (
            <RunRow
              key={run.run_id}
              locateActivity={locateActivity}
              run={run}
              runIndex={runIndex}
              setRunIndex={setRunIndex}
            />
          ))}
        </tbody>
      </table>
    </div>
      <GithubSvg className="mt-4 h-auto w-full" />
      {/* <GridSvg className="mt-4 h-auto w-full" /> */}
    </Suspense>
  </div>
);

export default SVGStat;
