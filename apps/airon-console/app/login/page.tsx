import Link from "next/link";
import { I } from "../../src/ui/primitives";

export default function Login() {
  return (
    <main className="login">
      <div className="welcome-frame">
        <div className="welcome-art">
          <img src="/brand/syntriass-lockup.png" alt="SYNTRIASS" width="812" height="591" />
        </div>
        <section className="welcome-entry" aria-labelledby="welcome-title">
          <div>
            <p className="welcome-product">AIRON Native</p>
            <h1 id="welcome-title">Workspace sign-in</h1>
            <p>Access your organization’s private AI workspace, knowledge vault and approved procedures.</p>
            <Link prefetch={false} className="btn primary" href="/signin-with-chatgpt?return_to=%2F" target="_top">
              Sign in to workspace <I n="right" size={17} />
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
