import { Link } from 'react-router-dom';
import { tv, type VariantProps } from 'tailwind-variants';

const category = tv({
  slots: {
    root: 'grid gap-3 justify-items-center px-2 py-[25px] bg-white w-48 border border-overlay border-solid rounded-[10px] hover:shadow-[2px_8px_6px_0px_var(--color-overlay)] hover:border-3 hover:border-blue-500 cursor-pointer',
    icone: 'text-[40px] text-blue-500',
    labelWrap: 'black-text text-sm text-center leading-5 w-full',
  },
});

const { root, icone, labelWrap } = category();

type CategorySchema = VariantProps<typeof category>;

interface CategoryCardProps extends CategorySchema {
  id: string;
  label: string;
  icon: React.ReactNode;
}

export default function CategoryCard({ label, icon, id }: CategoryCardProps) {
  return (
    <Link to={`/explorar?categoria=${id}`} className={root()}>
      <div className={icone()}>
        { icon }
      </div>

      <div className={labelWrap()}>
        <p>{label}</p>
      </div>
    </Link>
  );
}
