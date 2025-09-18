import { useEffect, useState } from "react";
import { getProfile } from "./api";

export default function Profile({ token }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function fetchProfile() {
      const data = await getProfile(token);
      setUser(data);
    }
    fetchProfile();
  }, [token]);

  if (!user) return <p>Загрузка...</p>;

  return (
    <div>
      <h2>Личный кабинет</h2>
      <p>ID: {user.id}</p>
      <p>Username: {user.username}</p>
      <p>Age: {user.age}</p>
      <p>Role: {user.role}</p>
    </div>
  );
}
