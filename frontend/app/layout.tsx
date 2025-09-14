import './globals.css'

export const metadata = {
  title: 'Mini RAG Application',
  description: 'A full-stack RAG application for document Q&A',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
