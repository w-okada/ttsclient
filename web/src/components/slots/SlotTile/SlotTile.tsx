import styles from "./SlotTile.module.css";

type Props = {
  index: number;
  name: string;
  ttsType: string | null;
  iconUrl: string | null;
  selected: boolean;
  onClick: () => void;
};

export const SlotTile = ({ index, name, ttsType, iconUrl, selected, onClick }: Props) => (
  <button className={`${styles.tile} ${selected ? styles.selected : ""}`} onClick={onClick}>
    <div className={styles.iconWrapper}>
      {iconUrl ? (
        <img className={styles.icon} src={iconUrl} alt={name} />
      ) : (
        <div className={styles.iconPlaceholder}>{index}</div>
      )}
    </div>
    {ttsType && <span className={styles.badge}>{ttsType}</span>}
    <span className={styles.name}>{name || `[${index}]`}</span>
  </button>
);
