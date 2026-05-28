import { BookOpen, ClipboardList, Trophy, User } from "lucide-react";
import { Link, Outlet } from "react-router-dom";

export function EmployeeLayout() {
  return (
    <div className="mobile-shell">
      <main className="mobile-main">
        <Outlet />
      </main>
      <nav className="bottom-tabs" aria-label="员工端导航">
        <Link to="/banks">
          <BookOpen size={18} />
          题库
        </Link>
        <Link to="/wrong">
          <ClipboardList size={18} />
          错题
        </Link>
        <Link to="/ranking">
          <Trophy size={18} />
          排行
        </Link>
        <Link to="/profile">
          <User size={18} />
          我的
        </Link>
      </nav>
    </div>
  );
}
