import type { FC, ReactElement } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from '../../hooks/store';
import { getUser } from '../../services/auth/slice';

type TProtectedRouteProps = {
  onlyUnAuth?: boolean;
  children: ReactElement;
};

export const ProtectedRoute: FC<TProtectedRouteProps> = ({
  onlyUnAuth = false,
  children
}: TProtectedRouteProps): ReactElement => {
  const user = useSelector(getUser);
  const location = useLocation();

  if (!onlyUnAuth && !user) {
    return <Navigate to='/login' state={{ from: location }} />;
  }

  if (onlyUnAuth && user) {
    const { from } = location.state ?? { from: { pathname: '/' } };
    return <Navigate to={from} />;
  }

  return children;
};

export const OnlyAuth = ProtectedRoute;
export const OnlyUnAuth = ({
  children
}: {
  children: ReactElement;
}): ReactElement => <ProtectedRoute onlyUnAuth children={children} />;