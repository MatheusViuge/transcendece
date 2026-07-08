import { Card as CardBase } from './Card';
import { CardBody } from './CardBody';
import { CardImage } from './CardImage';
import { CardProgress } from './CardProgress';
import { CardTitle } from './CardTitle';
import { CardAuthor, CardRating, CardPrice } from './CardDescription';

export const Card = Object.assign(CardBase, {
  Body: CardBody,
  Image: CardImage,
  Progress: CardProgress,
  Title: CardTitle,
  Author: CardAuthor,
  Price: CardPrice,
  Rating: CardRating,
});