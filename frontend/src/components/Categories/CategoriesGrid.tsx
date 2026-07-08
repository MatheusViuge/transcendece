import CategoryCard from './CategoryCard';
import { tv, type VariantProps } from 'tailwind-variants';
import { LuBriefcase, LuTrendingUp, LuPalette, LuCode } from "react-icons/lu";

const grid = tv({
  slots: {
    root: 'py-12 px-4 md:px-8 mx-auto max-w-[1300px]',
    headingWrap: 'content-stretch flex items-center justify-center px-0 py-0 w-full mb-6',
    heading: "black-text shrink-0 text-[16px] text-center",
    list: 'content-center flex flex-wrap gap-4 items-center justify-center w-full',
  },
});

const { root, headingWrap, heading, list } = grid();

type GridSchema = VariantProps<typeof grid>;

export default function CategoriesGrid(_props?: GridSchema) {
  type Category = {
    id: string;
    label: string;
    icon: React.ReactNode;
  };

  const categories: Category[] = [
    { id: 'programacao', label: 'Programação', icon: <LuCode /> },
    { id: 'design', label: 'Design', icon: <LuPalette /> },
    { id: 'negocios', label: 'Negocios', icon: <LuBriefcase /> },
    { id: 'marketing', label: 'Marketing', icon: <LuTrendingUp /> },
  ];

  return (
    <section className={root()}>
      <div className={headingWrap()}>
        <p className={heading()}>Pesquise por categoria</p>
      </div>

      <div className={list()}>
        {categories.map((cat) => (
          <CategoryCard key={cat.id} { ...cat } />
        ))}
      </div>
    </section>
  );
}
