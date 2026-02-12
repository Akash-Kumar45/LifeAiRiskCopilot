import { render, screen } from '@testing-library/react'
import TestPage from './test-page'

describe('TestPage', () => {
  it('renders test page content', () => {
    render(<TestPage />)
    expect(screen.getByText('Tailwind Test')).toBeInTheDocument()
    expect(screen.getByText('Styled Button')).toBeInTheDocument()
  })
})