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
  const handleClick = () => {
    if (runIndex === elementIndex) {
      setRunIndex(-1);
      locateActivity([]);
      return
    };
    setRunIndex(elementIndex);
    locateActivity([run.run_id]);
  };

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
      <td>{runTime}</td>
      <td className={styles.runDate}>
        <a href={run.relive_url} target="_blank" rel="noopener noreferrer">
          {run.start_date_local}
        </a>
      </td>
      <td>
        <button onClick={() => {
          const videoUrl = run.video_url;
          const modal = document.createElement('div');
          modal.innerHTML = `
            <style>
              .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999; /* 添加此行以确保模态框悬浮在最上面 */
              }
              .modal-content {
                width: 60%;
                height: 60%;
                background-color: #fff;
                border-radius: 10px;
                overflow: hidden; /* 添加此行以隐藏白边 */
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 添加此行以隐藏白边 */
                border: none; /* 添加此行以隐藏白边 */
              }
              .close-btn {
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 24px;
                cursor: pointer;
              }
            </style>
            <div class="modal">
              <div class="modal-content">
                <span class="close-btn">&times;</span>
                <iframe src="${videoUrl}" frameborder="0" width="100%" height="100%" allowfullscreen></iframe> <!-- 添加allowfullscreen以支持全屏播放 -->
              </div>
            </div>
          `;
          document.body.appendChild(modal);
          modal.querySelector('.modal')?.addEventListener('click', (e) => {
            if ((e.target as HTMLElement).classList.contains('modal') || (e.target as HTMLElement).classList.contains('close-btn')) {
              document.body.removeChild(modal);
            }
          });
        }}>relive</button>
      </td>
    </tr>
  );
};

export default RunRow;
