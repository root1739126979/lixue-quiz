import { BarChart3, Bot, Database, Download, ListChecks, Settings, Users } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

export function AdminLayout() {
  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <h1>砺学后台</h1>
        <NavLink to="/admin" end>
          <BarChart3 size={18} />
          数据看板
        </NavLink>
        <NavLink to="/admin/employees">
          <Users size={18} />
          员工管理
        </NavLink>
        <NavLink to="/admin/banks">
          <Database size={18} />
          题库管理
        </NavLink>
        <NavLink to="/admin/questions">
          <ListChecks size={18} />
          题目维护
        </NavLink>
        <NavLink to="/admin/points">
          <Settings size={18} />
          积分规则
        </NavLink>
        <NavLink to="/admin/llm">
          <Bot size={18} />
          AI讲解
        </NavLink>
        <NavLink to="/admin/exports">
          <Download size={18} />
          数据导出
        </NavLink>
      </aside>
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}
