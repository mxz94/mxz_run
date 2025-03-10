import { formatPace, colorFromType, formatRunTime, Activity, RunIds, convertMovingTime2Sec } from '@/utils/utils';
import styles from './style.module.css';

interface IRunRowProperties {
  elementIndex: number;
  locateActivity: (_runIds: RunIds) => void;
  run: Activity;
  runIndex: number;
  setRunIndex: (_ndex: number) => void;
  maxRecord: boolean;
}

const RunRow = ({ elementIndex, locateActivity, run, runIndex, setRunIndex, maxRecord }: IRunRowProperties) => {
  const distance = (run.distance / 1000.0).toFixed(2);
  const paceParts = run.average_speed ? formatPace(run.average_speed) : null;
  const heartRate = run.average_heartrate;
  const kmh = (run.distance * 3600.0 / convertMovingTime2Sec(run.moving_time)/1000.0).toFixed(2) + "km/h";
  const type = run.type;
  const runTime = formatRunTime(run.moving_time);
  const handleClick = runIndex != 0 ? () => {
    if (runIndex === elementIndex) {
      setRunIndex(-1);
      locateActivity([]);
      return
    };
    setRunIndex(elementIndex);
    locateActivity([run.run_id]);
  } : () => {};

  return (
    <tr
      className={`${styles.runRow} ${runIndex === elementIndex ? styles.selected : ''} ${maxRecord ? styles.maxRecord : ''}`}
      key={run.start_date_local}
      onClick={handleClick}
      style={{color: colorFromType(type)}}
    >
      <td>{run.name}</td>
      <td>{type}</td>
      <td>{distance}</td>
      <td>{paceParts}</td>
      <td>{kmh}</td>
      {/* <td>{heartRate && heartRate.toFixed(0)}</td> */}
      <td>
        <a href={run.relive_url} target="_blank" rel="noopener noreferrer">
          {runTime}
        </a>
      </td>
      <td className={styles.runDate}>
        <a href={run.video_url} target="_blank" rel="noopener noreferrer">
          {run.start_date_local}
        </a>
      </td>
    </tr>
  );
};

export default RunRow;
